# Generated by Django 2.2.9 on 2020-06-29 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_core', '0004_auto_20200204_1914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trigger',
            name='summary',
        ),
        migrations.AddField(
            model_name='trigger',
            name='description',
            field=models.CharField(default='', max_length=1024, verbose_name='说明'),
        ),
    ]
