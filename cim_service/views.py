from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Substation
from .serialisers import SubstationSerialiser

@api_view(['GET', 'POST'])
def api_substations(request):
    if request.method == 'GET':
        substations = Substation.objects.all()
        serialiser = SubstationSerialiser(substations, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        serialiser = SubstationSerialiser(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
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