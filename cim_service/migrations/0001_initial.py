# Generated by Django 4.0.5 on 2022-07-06 18:57

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('channels_and_devices_service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('998ac0ff-ec9a-4ddb-beb4-c653d904dbca'), editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('parent_company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cim_service.company')),
            ],
            options={
                'verbose_name': 'Компания',
                'verbose_name_plural': 'Компании',
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('23917758-c9ee-409e-9e6f-7dc543c32dc6'), editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('Read', 'Просмотр'), ('Edit', 'Редактирование'), ('Delete', 'Удаление'), ('Create', 'Создание')], max_length=10)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cim_service.company')),
            ],
        ),
        migrations.CreateModel(
            name='Substation',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('284bef6e-bcf7-419f-bd53-36b35cf259e3'), editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('is_station', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Энергообьект',
                'verbose_name_plural': 'Энергообъекты',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('3588ee05-9394-4205-b2b3-f57c40e59f7c'), editable=False, primary_key=True, serialize=False)),
                ('unit_id', models.UUIDField(db_index=True)),
                ('type', models.CharField(choices=[('Substation', 'Энергообьект'), ('Device', 'Устройство')], max_length=20)),
                ('companies', models.ManyToManyField(through='cim_service.Permission', to='cim_service.company')),
            ],
        ),
        migrations.AddField(
            model_name='permission',
            name='unit_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cim_service.unit'),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('fe8c6943-fefa-4ed5-8a43-0dc776237caf'), editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('Rx', 'Приёмник'), ('Tx', 'Передатчик'), ('Load_shedding', 'САОН'), ('Frequency_load_shedding', 'АЧР'), ('Stability_control_automatic', 'АПНУ')], max_length=50)),
                ('beams', models.ManyToManyField(to='channels_and_devices_service.beam')),
                ('substation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cim_service.substation')),
            ],
            options={
                'verbose_name': 'Устройство',
                'verbose_name_plural': 'Устройства',
            },
        ),
    ]
