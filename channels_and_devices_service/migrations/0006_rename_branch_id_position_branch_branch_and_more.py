# Generated by Django 4.0.5 on 2022-07-29 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels_and_devices_service', '0005_alter_node_branch_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='position_branch',
            old_name='branch_id',
            new_name='branch',
        ),
        migrations.RenameField(
            model_name='position_branch',
            old_name='position_id',
            new_name='position',
        ),
        migrations.AddField(
            model_name='position',
            name='branches',
            field=models.ManyToManyField(through='channels_and_devices_service.Position_Branch', to='channels_and_devices_service.branch'),
        ),
        migrations.AddField(
            model_name='position',
            name='changed_timestamp',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='position',
            name='is_normal',
            field=models.BooleanField(default=False),
        ),
    ]
