from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Node
from .serialisers import NodeSerialiser
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

