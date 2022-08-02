import datetime

from django.db.models import Q
from django.db.transaction import atomic
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Node, Beam, Branch, Selector, Position, Position_Branch
from .serialisers import NodeSerialiser, BeamSerialiser, SelectorSerialiser, SelectorPositionSerialiser
from rest_framework.response import Response

from cim_service.models import Device


@api_view(['GET', 'POST'])
def api_nodes(request):
    if request.method == 'GET':
        nodes = Node.objects.all()
        serialiser = NodeSerialiser(nodes, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        serialiser = NodeSerialiser(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def api_nodes_by_device(request, device_id):
    d = Device.objects.get(id=device_id)
    if request.method == 'GET':
        nodes = Node.objects.filter(device=d)
        serialiser = NodeSerialiser(nodes, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        count = request.data['count_nodes']
        for i in range(count):
            node = Node(local_number=i+1, device = d)
            node.save()
        nodes = Node.objects.filter(device=d)
        serialiser = NodeSerialiser(nodes, many=True)
        return Response(serialiser.data)


def get_nodes_by_device(device):
    nodes = Node.objects.filter(device=device)
    return nodes

@api_view(['GET', 'PUT', 'DELETE'])
def api_node_detail(request, id):
    node = Node.objects.get(id=id)
    if request.method == 'GET':
        serialiser = NodeSerialiser(node)
        return Response(serialiser.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serialiser = NodeSerialiser(node, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#каждый пучок может и должен быть подключен к двум устройствам
def get_beam_between_device(device1, device2):
    beams1 = device1.beams.all()
    beams2 = device2.beams.all()
    for b1 in beams1:
        for b2 in beams2:
            if b1.id == b2.id:
                return b1.id
    return False

def is_beam_inner(beam_id):
    b = Beam.objects.get(id=beam_id)
    devices = b.device_set.all()
    sub_id = devices[0].id
    for d in devices:
        sub = d.substation
        if sub_id != sub.id:
            return False
    return True

@api_view(['POST'])
def api_create_beam(request):
    b = Beam.objects.create()
    device1_id = request.data['device1_id']
    device2_id = request.data['device2_id']
    if device1_id is not None and device2_id is not None:
        d1 = Device.objects.get(id=device1_id)
        d2 = Device.objects.get(id=device2_id)
        b.save()
        d1.beams.add(b)
        d2.beams.add(b)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_delete_beam(request, id):
    b = Beam.objects.get(id=id)
    b.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def beams_by_device(device, mode):
    d = Device.objects.get(id=device.id)
    s=d.substation
    beams = d.beams.all()
    b_ids = []
    if mode == 'all':
        for b in beams:
            b_ids.append(b.id)
    elif mode == 'internal':
        d_next_ids_internal = []
        for b in beams:
            devices = b.device_set.all().exclude(id=device.id).filter(substation=s)
            for d1 in devices:
                d_next_ids_internal.append(d1.id)
            q = Q(device__id__in = d_next_ids_internal) & Q(id = b.id)

            internal_beams = Beam.objects.filter(q)
            for b in internal_beams:
                b_ids.append(b.id)
    elif mode == 'external':
        d_next_ids_external = []
        for b in beams:
            devices = b.device_set.all().exclude(id=device.id).exclude(substation=s)
            for d1 in devices:
                d_next_ids_external.append(d1.id)
            q = Q(device__id__in = d_next_ids_external) & Q(id = b.id)

            external_beams = Beam.objects.filter(q)
            for b in external_beams:
                b_ids.append(b.id)
    return b_ids

@api_view(['POST'])
def api_create_branch(request):
    node1_id = request.data['node1_id']
    node2_id = request.data['node2_id']
    direction = request.data['direction']
    if node1_id is not None and node2_id is not None:
        n1 = Node.objects.get(id=node1_id)
        n2 = Node.objects.get(id=node2_id)
        d1 = n1.device
        d2 = n2.device
        beam_id = get_beam_between_device(d1, d2)
        beam = Beam.objects.get(id=beam_id)
        br = Branch.objects.create(beam=beam)
        if direction == 'direct':
            n1.branches.add(br, through_defaults={'type': 'direct'})
            n2.branches.add(br, through_defaults={'type': 'reverse'})
        elif direction == 'reverse':
            n1.branches.add(br, through_defaults={'type': 'reverse'})
            n2.branches.add(br, through_defaults={'type': 'direct'})
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_delete_branch(request, id):
    br = Branch.objects.get(id=id)
    br.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

def branch_by_node(node, mode):
    d = node.device
    s=d.substation
    branches = node.branches.all()
    br_ids = []
    if mode == 'all':
        for br in branches:
            br_ids.append(br.id)
    elif mode == 'internal':
        n_next_ids_internal = []
        for br in branches:
            nodes = br.node_set.all().exclude(id=node.id).filter(device__substation=s)
            for n1 in nodes:
                n_next_ids_internal.append(n1.id)
            q = Q(node__id__in = n_next_ids_internal) & Q(id = br.id)

            internal_branches = Branch.objects.filter(q)
            for br in internal_branches:
                br_ids.append(br.id)
    elif mode == 'external':
        n_next_ids_external = []
        for br in branches:
            nodes = br.node_set.all().exclude(id=node.id).exclude(device__substation=s)
            for n1 in nodes:
                n_next_ids_external.append(n1.id)
            q = Q(node__id__in = n_next_ids_external) & Q(id = br.id)

            external_branches = Branch.objects.filter(q)
            for br in external_branches:
                br_ids.append(br.id)
    return br_ids


@api_view(['GET'])
def api_table_for_device(request, device_id):
    d = Device.objects.get(id=device_id)
    sub = d.substation

    data = {
        "device_id": d.id,
        "device_name": d.name,
        "device_type": d.type,
        "substation_id": sub.id,
        "substation_name": sub.name
    }

    nodes = get_nodes_by_device(d)
    node_list = []
    for n in nodes:
        node_dict = {
            "node_id": n.id,
            "node_local_number": n.local_number,
            "node_name": n.name
        }

        branches = n.branches.all()
        branch_list = []
        for br in branches:
            next_node = Node.objects.filter(branches__id=br.id).exclude(id=n.id).first()
            branch_dict = {
                "beam_id": br.beam.id,
                "branch_id": br.id,
                "branch_in_service": br.in_service,
                "next_node_id": next_node.id,
                "next_node_local_number": next_node.local_number,
                "next_node_name": next_node.name
            }
            branch_list.append(branch_dict)
        node_dict["branches"] = branch_list
        node_list.append(node_dict)
    data["nodes"] = node_list

    beam_list = []
    beams = Beam.objects.filter(device__id=device_id)
    for b in beams:
        next_device = Device.objects.filter(beams__id=b.id).exclude(id=d.id).first()
        if next_device.substation.id == sub.id:
            beam_dict = {
                "beam_id": b.id,
                "beam_in_service": b.in_service,
                "beam_type": "internal",
                "next_device_id": next_device.id,
                "next_device_name": next_device.name
            }
        else:
            beam_dict = {
                "beam_id": b.id,
                "beam_in_service": b.in_service,
                "beam_type": "external",
                "next_device_id": next_device.id,
                "next_device_name": next_device.name,
                "next_substation_id": next_device.substation.id,
                "next_substation_name": next_device.substation.name
            }
        beam_list.append(beam_dict)
    data["beams"] = beam_list

    return JsonResponse(data)

@api_view(['GET'])
def api_route_by_node(request, node_id):
    n = Node.objects.get(id=node_id)
    data = {}
    data["segments"] = get_out_route_by_device(n, 1)
    for ns in get_in_route_by_device(n, -1):
        data["segments"].append(ns)
    return JsonResponse(data)

def get_out_route_by_device(node, level):
    segment_list=[]
    d = node.device
    sub = d.substation
    segment_dict = {}
    # обработка ИСХОДЯЩИХ ветвей для запрошенного узла
    q = Q(node__id=node.id) & Q(node_branch__type='direct')
    out_branches = Branch.objects.filter(q)
    for out_br in out_branches:
        next_n = Node.objects.filter(branches__id = out_br.id).exclude(id=node.id).first()
        next_d = next_n.device
        next_sub = next_d.substation
        segment_dict["start_node_id"] = node.id
        segment_dict["start_node_name"] = node.name
        segment_dict["start_node_local_number"] = node.local_number
        segment_dict["start_device_id"] = d.id
        segment_dict["start_device_name"] = d.name
        segment_dict["start_subsnation_id"] = sub.id
        segment_dict["start_subsnation_name"] = sub.name
        segment_dict["end_node_id"] = next_n.id
        segment_dict["end_node_name"] = next_n.name
        segment_dict["end_node_local_number"] = next_n.local_number
        segment_dict["end_device_id"] = next_d.id
        segment_dict["end_device_name"] = next_d.name
        segment_dict["end_subsnation_id"] = next_sub.id
        segment_dict["end_subsnation_name"] = next_sub.name
        segment_dict["in_service"] = out_br.in_service
        if sub.id == next_sub.id:
            segment_dict["type"] = "internal"
        else:
            segment_dict["type"] = "external"
        segment_dict["level"] = level
        segment_list.append(segment_dict)
        list_next_segments = get_out_route_by_device(next_n, level+1)
        for ns in list_next_segments:
            segment_list.append(ns)


    return segment_list


def get_in_route_by_device(node, level):
    segment_list=[]
    d = node.device
    sub = d.substation
    segment_dict = {}
    # обработка ВХОДЯЩИХ ветвей для запрошенного узла
    q = Q(node__id=node.id) & Q(node_branch__type='reverse')
    in_branches = Branch.objects.filter(q)
    for in_br in in_branches:
        next_n = Node.objects.filter(branches__id = in_br.id).exclude(id=node.id).first()
        next_d = next_n.device
        next_sub = next_d.substation
        segment_dict["start_node_id"] = next_n.id
        segment_dict["start_node_name"] = next_n.name
        segment_dict["start_node_local_number"] = next_n.local_number
        segment_dict["start_device_id"] = next_d.id
        segment_dict["start_device_name"] = next_d.name
        segment_dict["start_subsnation_id"] = next_sub.id
        segment_dict["start_subsnation_name"] = next_sub.name
        segment_dict["end_node_id"] = node.id
        segment_dict["end_node_name"] = node.name
        segment_dict["end_node_local_number"] = node.local_number
        segment_dict["end_device_id"] = d.id
        segment_dict["end_device_name"] = d.name
        segment_dict["end_subsnation_id"] = sub.id
        segment_dict["end_subsnation_name"] = sub.name
        segment_dict["in_service"] = in_br.in_service
        if sub.id == next_sub.id:
            segment_dict["type"] = "internal"
        else:
            segment_dict["type"] = "external"
        segment_dict["level"] = level
        segment_list.append(segment_dict)
        list_next_segments = get_in_route_by_device(next_n, level-1)
        for ns in list_next_segments:
            segment_list.append(ns)
    return segment_list

@api_view(['GET', 'POST'])
def api_selectors(request):
    if request.method == 'GET':
        selectors = Selector.objects.all()
        serialiser = SelectorSerialiser(selectors, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        serialiser = SelectorSerialiser(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def api_selectors_by_device(request, device_id):
    selectors = Selector.objects.filter(device__id = device_id)
    serialiser = SelectorSerialiser(selectors, many=True)
    return Response(serialiser.data)

@api_view(['GET', 'PUT', 'DELETE', 'PATCH'])
def api_selector_detail(request, id):
    selector = Selector.objects.get(id=id)
    if request.method == 'GET':
        serialiser = SelectorSerialiser(selector)
        return Response(serialiser.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serialiser = SelectorSerialiser(selector, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        selector.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def api_positions(request):
    if request.method == 'GET':
        positions = Position.objects.all()
        serialiser = SelectorPositionSerialiser(positions, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        serialiser = SelectorPositionSerialiser(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE', 'PATCH'])
def api_position_detail(request, id):
    position = Position.objects.get(id=id)
    if request.method == 'GET':
        serialiser = SelectorPositionSerialiser(position)
        return Response(serialiser.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serialiser = SelectorPositionSerialiser(position, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        position.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def positions_by_selector(selector_id):
    positions = Position.objects.filter(selector__id = selector_id)
    return positions

@atomic
def activate_position(position):
    next_positions = Position.objects.filter(selector = position.selector).exclude(id = position.id)
    timestamp = datetime.datetime.now()
    for n_pos in next_positions:
        n_pos.in_service = False
        n_pos.changed_timestamp = timestamp
        n_pos.save()
    #q = Q(position__id=position.id) & Q(position_branch__type='on')
    #branch_on_set = Branch.objects.filter(q)
    #for br_on in branch_on_set:
    #    br_on.in_service = True
    #    br_on.save()
    #q = Q(position__id=position.id) & Q(position_branch__type='off')
    #branch_off_set = Branch.objects.filter(q)
    #for br_off in branch_off_set:
    #    br_off.in_service = False
    #    br_off.save()
    position.in_service = True
    position.changed_timestamp = timestamp
    position.save()
    q = Q(position__id=position.id) & Q(position_branch__type='on')
    branch_on_set = Branch.objects.filter(q)
    for br_on in branch_on_set:
        br_on.in_service = True
        br_on.save()
    q = Q(position__id=position.id) & Q(position_branch__type='off')
    branch_off_set = Branch.objects.filter(q)
    for br_off in branch_off_set:
        br_off.in_service = False
        br_off.save()

@api_view(['POST'])
def api_connect_position_branch(request):
    position_id = request.data['position_id']
    branch_id = request.data['branch_id']
    state = request.data['state']
    p = Position.objects.get(id=position_id)
    br = Branch.objects.get(id=branch_id)
    if p != None and br != None:
        if state == 'on':
            p.branches.add(br, through_defaults={'type': 'on'})
        elif state == 'off':
            p.branches.add(br, through_defaults={'type': 'off'})
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def api_activate_position(request, position_id):
    p = Position.objects.get(id=position_id)
    activate_position(p)
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def api_select_normal_state(request, position_id):
    p = Position.objects.get(id=position_id)
    select_normal_state(p)
    return Response(status=status.HTTP_200_OK)

@atomic
def select_normal_state(position):
    next_positions = Position.objects.filter(selector=position.selector).exclude(id=position.id)
    #timestamp = datetime.datetime.now()
    for n_pos in next_positions:
        n_pos.is_normal = False
        n_pos.save()
    position.is_normal = True
    position.save()


@api_view(['GET'])
def api_selectors_for_device(request, device_id):
    d = Device.objects.get(id=device_id)

    data = {}
    selectors = Selector.objects.filter(device=d)
    selectors_list = []
    for sel in selectors:
        selector_dict ={
            "selector_id": sel.id,
            "selector_short_name": sel.short_name,
            "selector_name": sel.name
        }
        positions = Position.objects.filter(selector=sel)
        positions_list=[]
        for pos in positions:
            position_dict = {
                "position_id": pos.id,
                "position_name": pos.name,
                "changed_timestamp": pos.changed_timestamp,
                "in_service": pos.in_service,
                "is_normal": pos.is_normal
            }
            branches = Branch.objects.filter(position__id = pos.id)
            branches_list = []
            for br in branches:
                br_dict = {
                    "branch_id": br.id,
                    "type": Position_Branch.objects.filter(position = pos).filter(branch = br).first().type
                }
                branches_list.append(br_dict)
            position_dict["branches"] = branches_list
            positions_list.append(position_dict)
        selector_dict["positions"] = positions_list
        selectors_list.append(selector_dict)
    data["selectors"] = selectors_list
    return JsonResponse(data)