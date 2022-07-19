from rest_framework import serializers
from .models import Substation, Unit, Company, Permission, Device


class SubstationSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Substation
        fields = ('id','name', 'is_station')

class CompanySerialiser(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id','name', 'parent_company')

class UnitSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id','unit_id', 'type', 'companies')

class PermissionSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id','unit_id','company_id', 'type')

class DeviceSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id','name', 'substation', 'type')