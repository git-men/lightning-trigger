# Generated by Django 2.2.17 on 2021-01-28 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_core', '0010_auto_20210128_0207'),
    ]

    operations = [
        migrations.AddField(
            model_name='triggeraction',
            name='description',
            field=models.CharField(blank=True, max_length=140, null=True, verbose_name='描述'),
        ),
    ]
