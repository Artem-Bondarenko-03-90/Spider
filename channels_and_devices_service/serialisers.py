from rest_framework import serializers
from .models import Node

class NodeSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ('id','name', 'local_number', 'device')