# Generated by Django 4.0.5 on 2022-07-10 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cim_service', '0002_alter_company_id_alter_device_id_alter_permission_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='parent_company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cim_service.company'),
        ),
    ]