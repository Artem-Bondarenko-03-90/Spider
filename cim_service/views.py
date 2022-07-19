from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Substation, Unit, Company, Permission, Device
from .serialisers import SubstationSerialiser, CompanySerialiser, PermissionSerialiser, DeviceSerialiser


@api_view(['GET', 'POST'])
def api_substations(request):
    if request.method == 'GET':
        substations = Substation.objects.all()
        serialiser_substation = SubstationSerialiser(substations, many=True)
        return Response(serialiser_substation.data)
    elif request.method == 'POST':
        serialiser_substation = SubstationSerialiser(data=request.data)
        if serialiser_substation.is_valid():
            serialiser_substation.save()
            # создаем запись Unit
            u = Unit(unit_id = serialiser_substation.data['id'], type = 'Substation')
            u.save()
            #print(serialiser_substation.data['id'])
            return Response(serialiser_substation.data, status=status.HTTP_201_CREATED)
        return Response(serialiser_substation.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def api_substation_detail(request, id):
    substation = Substation.objects.get(id=id)
    if request.method == 'GET':
        serialiser = SubstationSerialiser(substation)
        return Response(serialiser.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serialiser = SubstationSerialiser(substation, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        substation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def api_companies(request):
    if request.method == 'GET':
        company = Company.objects.all()
        serialiser = CompanySerialiser(company, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        serialiser = CompanySerialiser(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def api_company_detail(request, id):
    company = Company.objects.get(id=id)
    if request.method == 'GET':
        serialiser = CompanySerialiser(company)
        return Response(serialiser.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serialiser = CompanySerialiser(company, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Автоматически должны создаваться permission с типом read для родительских компаний
@api_view(['GET', 'POST'])
def api_permissions(request):
    if request.method == 'GET':
        p = Permission.objects.all()
        serialiser = PermissionSerialiser(p, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        if request.data['device_id'] is None and request.data['substation_id'] is not None:
            u = Unit.objects.get(unit_id=request.data['substation_id'])
            d = {
                    'unit_id': u.id,
                    'company_id': request.data['company_id'],
                    'type': request.data['type']
                 }
            #рекурсивно добавим права на чтение для родительских компаний
            set_permission_for_parent_companies(request.data['company_id'], u.id)

        elif request.data['substation_id'] is None and request.data['device_id'] is not None:
            u = Unit.objects.get(unit_id=request.data['device_id'])
            d = {
                'unit_id': u.id,
                'company_id': request.data['company_id'],
                'type': request.data['type']
            }
            set_permission_for_parent_companies(request.data['company_id'], u.id)

        elif request.data['device_id'] is None and request.data['substation_id'] is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.data['device_id'] is not None and request.data['substation_id'] is not None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serialiser = PermissionSerialiser(data=d)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)


def set_permission_for_parent_companies(children_company_id, unit_id):
    ch_c = Company.objects.get(id=children_company_id)
    if ch_c.parent_company is not None:
        parent_company_id = ch_c.parent_company.id
        d_parent = {
            'unit_id': unit_id,
            'company_id': parent_company_id,
            'type': 'Read'
        }
        serialiser_parent_company = PermissionSerialiser(data=d_parent)
        if serialiser_parent_company.is_valid():
            serialiser_parent_company.save()
            set_permission_for_parent_companies(parent_company_id, unit_id)




@api_view(['GET'])
def api_permissions_by_company_for_substations(request, company_id):
    company = Company.objects.get(id=company_id)
    units = company.unit_set.filter(type='Substation')
    list =[]
    for u in units:
        list.append(u.unit_id)
    substations = Substation.objects.filter(pk__in=list)
    serialiser = SubstationSerialiser(substations, many=True)
    return Response(serialiser.data)

# получить компанию текущего пользователя
@api_view(['GET'])
def api_my_company(request):
    pass

@api_view(['GET', 'POST'])
def api_devices(request):
    if request.method == 'GET':
        devices = Device.objects.all()
        serialiser = DeviceSerialiser(devices, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        serialiser = DeviceSerialiser(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            # создаем запись Unit
            u = Unit(unit_id = serialiser.data['id'], type = 'Device')
            u.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def api_device_detail(request, id):
    device = Device.objects.get(id=id)
    if request.method == 'GET':
        serialiser = DeviceSerialiser(device)
        return Response(serialiser.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serialiser = DeviceSerialiser(device, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def api_devices_by_substation(request, substation_id):
    s = Substation.objects.get(id=substation_id)
    devices = Device.objects.filter(substation = s)
    serialiser = DeviceSerialiser(devices, many=True)
    return Response(serialiser.data)

@api_view(['GET', 'POST'])
def api_nodes(request):
    pass

@api_view(['GET', 'PUT', 'DELETE'])
def api_node_detail(request, id):
    pass

@api_view(['POST'])
def api_nodes_by_device(request, device_id):
    pass