from django.db import models
import uuid

# Node
class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=150)
    local_number = models.PositiveSmallIntegerField()
    device = models.ForeignKey('cim_service.Device', on_delete=models.PROTECT)
    branches = models.ManyToManyField('Branch', through='Node_Branch', through_fields=('node_id', 'branch_id'))

# Beam
class Beam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    in_service = models.BooleanField(default=True)

# Branch
class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    in_service = models.BooleanField(default=True)
    beam = models.ForeignKey(Beam, on_delete=models.PROTECT)

# Selector
class Selector(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    short_name = models.CharField(max_length=10)
    name = models.CharField(max_length=150)
    device = models.ForeignKey('cim_service.Device', on_delete=models.PROTECT)

#Position
class Position(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=30)
    in_service = models.BooleanField(default=True)
    selector = models.ForeignKey(Selector, on_delete=models.PROTECT)

#Node_Branch
class Node_Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    node_id = models.ForeignKey(Node, on_delete=models.CASCADE)
    branch_id = models.ForeignKey(Branch, on_delete=models.CASCADE)
    TYPES = (
        ('input', 'Вход'),
        ('output', 'Выход'),
    )
    type = models.CharField(max_length=10, choices=TYPES)

#Position_Branch
class Position_Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    position_id = models.ForeignKey(Position, on_delete=models.CASCADE)
    branch_id = models.ForeignKey(Branch, on_delete=models.CASCADE)
    TYPES = (
        ('on', 'Вкл'),
        ('off', 'Откл'),
    )
    type = models.CharField(max_length=5, choices=TYPES, default='off')
