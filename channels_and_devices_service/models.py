from django.db import models
import uuid

# Node
class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, null=True)
    local_number = models.PositiveSmallIntegerField(null=True)
    device = models.ForeignKey('cim_service.Device', on_delete=models.PROTECT)
    branches = models.ManyToManyField('Branch', through='Node_Branch', through_fields=('node_id', 'branch_id'))
    equipments = models.ManyToManyField('cim_service.Equipment', through='EquipmentControlAction', through_fields=('node', 'equipment'))
    class Meta:
        verbose_name = 'Узел'
        verbose_name_plural = 'Узлы'

# Beam
class Beam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    in_service = models.BooleanField(default=True)
    class Meta:
        verbose_name = 'Пучок'
        verbose_name_plural = 'Пучки'

# Branch
class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    in_service = models.BooleanField(default=True)
    beam = models.ForeignKey(Beam, on_delete=models.PROTECT)
    class Meta:
        verbose_name = 'Ветвь'
        verbose_name_plural = 'Ветви'

# Selector
class Selector(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_name = models.CharField(max_length=10)
    name = models.CharField(max_length=150)
    device = models.ForeignKey('cim_service.Device', on_delete=models.PROTECT)
    class Meta:
        verbose_name = 'Переключатель'
        verbose_name_plural = 'Переключатели'

#Position
class Position(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)
    in_service = models.BooleanField(default=True)
    is_normal = models.BooleanField(default=False)
    selector = models.ForeignKey(Selector, on_delete=models.PROTECT)
    changed_timestamp = models.DateTimeField(null=True)
    branches = models.ManyToManyField('Branch', through='Position_Branch', through_fields=('position', 'branch'))
    class Meta:
        verbose_name = 'Положение переключателя'
        verbose_name_plural = 'Положения переключателей'

#Node_Branch
class Node_Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_id = models.ForeignKey(Node, on_delete=models.CASCADE)
    branch_id = models.ForeignKey(Branch, on_delete=models.CASCADE)
    TYPES = (
        ('direct', 'Прямо'),
        ('reverse', 'Обратно'),
    )
    type = models.CharField(max_length=10, choices=TYPES)

#Position_Branch
class Position_Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    TYPES = (
        ('on', 'Вкл'),
        ('off', 'Откл'),
    )
    type = models.CharField(max_length=5, choices=TYPES, default='off')


# EquipmentControlAction
class EquipmentControlAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    equipment = models.ForeignKey('cim_service.Equipment', on_delete=models.CASCADE)
    ACTION_TYPES = (
        ('turn_on', 'Включение'),
        ('turn_off', 'Отключение'),
        ('generation_step_down', 'Ступенчатое снижение генерации')
    )
    action_type = models.CharField(max_length=40, choices=ACTION_TYPES, default='turn_off')