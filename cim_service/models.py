from django.db import models
import uuid

# Substation
class Substation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    is_station = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'Энергообьект'
        verbose_name_plural = 'Энергообъекты'

# Company
class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    parent_company = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, default=None)
    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'


# Unit
class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit_id = models.UUIDField(db_index=True) # в это поле просто копируется id нужной сущности
    TYPES = (
        ('Substation', 'Энергообьект'),
        ('Device', 'Устройство'),
    )
    type = models.CharField(max_length=20, choices=TYPES)
    companies = models.ManyToManyField(Company, through='Permission', through_fields=('unit_id', 'company_id'))

#Permission
class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit_id = models.ForeignKey(Unit, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    TYPES = (
        ('Read', 'Просмотр'),
        ('Edit', 'Редактирование'),
        ('Delete', 'Удаление'),
        ('Create', 'Создание'),
    )
    type = models.CharField(max_length=10, choices=TYPES)
    class Meta():
        unique_together = ('unit_id', 'company_id', 'type')

#Device
class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    TYPES = (
        ('Rx', 'Приёмник'),
        ('Tx', 'Передатчик'),
        ('Load_shedding', 'САОН'),
        ('Frequency_load_shedding', 'АЧР'),
        ('Stability_control_automatic', 'АПНУ'),
        ('Over_power_automatic', 'АОПО'),
    )
    type = models.CharField(max_length=50, choices=TYPES)
    substation = models.ForeignKey(Substation, on_delete=models.PROTECT)
    beams = models.ManyToManyField('channels_and_devices_service.Beam')
    class Meta:
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'
