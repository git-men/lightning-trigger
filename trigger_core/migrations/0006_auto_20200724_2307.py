# Generated by Django 2.2.9 on 2020-07-24 23:07

import api_basebone.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_core', '0005_auto_20200629_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='triggeraction',
            name='receiver_filters',
            field=api_basebone.core.fields.JSONField(blank=True, default=[], verbose_name='接收者的过滤条件'),
        ),
        migrations.AddField(
            model_name='triggeraction',
            name='subject_template',
            field=models.CharField(default='', max_length=100, verbose_name='标题模板'),
        ),
        migrations.AddField(
            model_name='triggeraction',
            name='text_template',
            field=models.TextField(default='', verbose_name='正文模板'),
        ),
        migrations.AlterField(
            model_name='triggeraction',
            name='action',
            field=models.CharField(choices=[('create', '创建记录'), ('update', '更新记录'), ('delete', '删除记录'), ('send_email', '发送邮件')], max_length=20, verbose_name='条件类型'),
        ),
    ]