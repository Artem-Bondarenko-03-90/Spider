from rest_framework import serializers
from .models import Substation

class SubstationSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Substation
        fields = ('id','name', 'is_station')