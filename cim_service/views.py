from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Substation, Unit, Company, Permission, Device, Switchgear, Equipment, Profile
from .serialisers import SubstationSerialiser, CompanySerialiser, DeviceSerialiser, \
    SwitchgearSerialiser, EquipmentSerialiser, PermissionSerialiser, UserSerialiser
from channels_and_devices_service.views import beams_by_device
from django.contrib.auth.models import User


@api_view(['GET', 'POST'])
def api_substations(request):
    if request.method == 'GET':
        user_company = my_company(request.user)
        units_dict = get_ls_units_with_permission(user_company, 'Substation')
        data = {"substations": []}
        for u in units_dict.keys():
            s = Substation.objects.get(id=u)
            sub_dict={}
            sub_dict["id"]=s.id
            sub_dict["name"] = s.name
            sub_dict["is_station"] = s.is_station
            sub_dict["permission"] = units_dict[u]
            data["substations"].append(sub_dict)
        return JsonResponse(data)
    elif request.method == 'POST':
        serialiser_substation = SubstationSerialiser(data=request.data)
        if serialiser_substation.is_valid():
            serialiser_substation.save()
            # создаем запись Unit
            u = Unit(unit_id = serialiser_substation.data['id'], type = 'Substation')
            u.save()

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
        unit_ids = request.data['units']
        company_id = request.data['company_id']
        company = Company.objects.get(id=company_id)
        permission_type = request.data['permission_type']
        action = request.data['action']
        if action:
            q = Q(unit_id__unit_id__in=unit_ids) & Q(company_id__id=company_id) & Q(type=permission_type)
            permissions = Permission.objects.filter(q)
            permissions_exclude = []
            for p in permissions:
                permissions_exclude.append(p.unit_id.unit_id)

            for unit_id in unit_ids:
                if unit_id not in permissions_exclude:
                    u = Unit.objects.get(unit_id=unit_id)
                    d = {
                         'unit_id': u.id,
                         'company_id': company_id,
                         'type': permission_type
                        }
                    serialiser = PermissionSerialiser(data=d)
                    if serialiser.is_valid():
                        serialiser.save()
                    # рекурсивно добавим права на чтение для родительских компаний
                    set_permission_for_parent_companies(company_id, u.id)
            q = Q(unit_id__unit_id__in=unit_ids) & Q(company_id__id=company_id) & Q(type=permission_type)
            permissions = Permission.objects.filter(q)
            serialiser = PermissionSerialiser(permissions, many=True)
            return Response(serialiser.data)
        else:
            q = Q(unit_id__unit_id__in=unit_ids) & Q(company_id__id=company_id) & Q(type=permission_type)
            permissions = Permission.objects.filter(q)
            for perm in permissions:
                perm.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)



def set_permission_for_parent_companies(children_company_id, unit_id):
    ch_c = Company.objects.get(id=children_company_id)
    if ch_c.parent_company is not None:
        parent_company_id = ch_c.parent_company.id
        d = {
            'unit_id': unit_id,
            'company_id': parent_company_id,
            'type': 'Read'
        }
        serialiser = PermissionSerialiser(data=d)
        if serialiser.is_valid():
            serialiser.save()
        set_permission_for_parent_companies(parent_company_id, unit_id)




# @api_view(['GET'])
# def api_permissions_by_company_for_substations(request, company_id):
#     company = Company.objects.get(id=company_id)
#     units = company.unit_set.filter(type='Substation')
#     list =[]
#     for u in units:
#         list.append(u.unit_id)
#     substations = Substation.objects.filter(pk__in=list)
#     serialiser = SubstationSerialiser(substations, many=True)
#     return Response(serialiser.data)


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
def api_switchgear(request):
    if request.method == 'GET':
        switchgears = Switchgear.objects.all()
        serialiser = SwitchgearSerialiser(switchgears, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        serialiser = SwitchgearSerialiser(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            # создаем запись Unit
            u = Unit(unit_id = serialiser.data['id'], type = 'Switchergear')
            u.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def api_switchgear_detail(request, id):
    sw = Switchgear.objects.get(id=id)
    if request.method == 'GET':
        serialiser = SwitchgearSerialiser(sw)
        return Response(serialiser.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serialiser = SwitchgearSerialiser(sw, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        sw.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def api_switchgear_by_substation(request, substation_id):
    s = Substation.objects.get(id=substation_id)
    switchgears = Switchgear.objects.filter(substation = s)
    serialiser = SwitchgearSerialiser(switchgears, many=True)
    return Response(serialiser.data)


@api_view(['GET', 'POST'])
def api_equipment(request):
    if request.method == 'GET':
        equipments = Equipment.objects.all()
        serialiser = EquipmentSerialiser(equipments, many=True)
        return Response(serialiser.data)
    elif request.method == 'POST':
        serialiser = EquipmentSerialiser(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            # создаем запись Unit
            u = Unit(unit_id=serialiser.data['id'], type='Equipment')
            u.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def api_equipment_detail(request, id):
    e = Equipment.objects.get(id=id)
    if request.method == 'GET':
        serialiser = EquipmentSerialiser(e)
        return Response(serialiser.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serialiser = EquipmentSerialiser(e, data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        e.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def api_equipment_by_switchgear(request, switchgear_id):
    sw = Switchgear.objects.get(id=switchgear_id)
    equipments = Equipment.objects.filter(switchgear = sw)
    serialiser = EquipmentSerialiser(equipments, many=True)
    return Response(serialiser.data)

@api_view(['POST'])
def api_create_user(request):
    login = request.data['login']
    password = request.data['password']
    company_id = request.data['company_id']
    company = Company.objects.get(id=company_id)
    user = User.objects.create_user(login, password=password, is_staff=True)
    profile = Profile(company=company, user=user)
    user.save()
    profile.save()
    serialiser = UserSerialiser(user)
    return Response(serialiser.data)

# получить компанию текущего пользователя

def my_company(user):
    company = user.profile.company
    return company

def get_ls_units_with_permission(company, unit_type):
    user_company = company
    units = user_company.unit_set.filter(type=unit_type)
    perms_read_ls = []
    perms_edit_ls = []
    for u in units:
        permissions_read = Permission.objects.filter(unit_id=u).filter(company_id=user_company).filter(type='Read')
        for pr in permissions_read:
            perms_read_ls.append(pr.unit_id.unit_id)
        permissions_edit = Permission.objects.filter(unit_id=u).filter(company_id=user_company).filter(
            type__in=('Edit', 'Create', 'Delete'))
        for pe in permissions_edit:
            perms_edit_ls.append(pe.unit_id.unit_id)
    unit_read = Unit.objects.filter(unit_id__in=perms_read_ls)
    unit_edit = Unit.objects.filter(unit_id__in=perms_edit_ls)
    data = {}
    for ue in unit_edit:
        data[ue.unit_id] = 'edit'
    for ur in unit_read:
        if ur not in unit_edit:
            data[ur.unit_id] = 'read'
    return data