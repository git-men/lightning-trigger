# Generated by Django 2.2.9 on 2020-02-03 15:33

import api_basebone.core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trigger',
            name='condition',
            field=api_basebone.core.fields.JSONField(default={}, verbose_name='触发条件'),
        ),
        migrations.DeleteModel(
            name='TriggerCondition',
        ),
    ]
