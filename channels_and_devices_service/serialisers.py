from rest_framework import serializers
from .models import Node, Beam


class NodeSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ('id','name', 'local_number', 'device')

class BeamSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Beam
        fields = ('id','in_service')