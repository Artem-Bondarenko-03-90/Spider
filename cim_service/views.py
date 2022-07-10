from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Substation, Unit, Company, Permission
from .serialisers import SubstationSerialiser, CompanySerialiser, PermissionSerialiser

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

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
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

@api_view(['GET', 'POST'])
def api_permissions(request):
    if request.method == 'GET':
        p = Permission.objects.all()
        serialiser = PermissionSerialiser(p, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        if 'substation_id' in request.data:
            u = Unit.objects.get(unit_id=request.data['substation_id'])
            d = {
                    'unit_id': u.id,
                    'company_id': request.data['company_id'],
                    'type': request.data['type']
                 }
        elif 'device_id' in request.data:
            u = Unit.objects.get(unit_id=request.data['device_id'])
            d = {
                'unit_id': u.id,
                'company_id': request.data['company_id'],
                'type': request.data['type']
            }
        serialiser = PermissionSerialiser(data=d)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)