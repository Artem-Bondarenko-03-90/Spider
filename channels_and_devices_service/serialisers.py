from rest_framework import serializers
from .models import Node, Beam, Selector, Position


class NodeSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ('id','name', 'local_number', 'device')

class BeamSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Beam
        fields = ('id','in_service')

class SelectorSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Selector
        fields = ('id', 'short_name', 'name', 'device')

class SelectorPositionSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id', 'name', 'in_service', 'selector')