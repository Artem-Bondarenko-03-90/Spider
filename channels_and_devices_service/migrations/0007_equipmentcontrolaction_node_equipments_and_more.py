# Generated by Django 4.0.5 on 2022-08-16 18:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('cim_service', '0006_equipment_feeder_switchgear_equipment_switchgear'),
        ('channels_and_devices_service', '0006_rename_branch_id_position_branch_branch_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentControlAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action_type', models.CharField(choices=[('turn_on', 'Включение'), ('turn_off', 'Отключение'), ('generation_step_down', 'Ступенчатое снижение генерации')], default='turn_off', max_length=40)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cim_service.equipment')),
            ],
        ),
        migrations.AddField(
            model_name='node',
            name='equipments',
            field=models.ManyToManyField(through='channels_and_devices_service.EquipmentControlAction', to='cim_service.equipment'),
        ),
        migrations.AddField(
            model_name='equipmentcontrolaction',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='channels_and_devices_service.node'),
        ),
    ]