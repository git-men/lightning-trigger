# Generated by Django 2.2.9 on 2020-11-23 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_core', '0008_auto_20201119_0321'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='triggeraction',
            options={'verbose_name': '触发动作', 'verbose_name_plural': '触发动作'},
        ),
        migrations.AlterField(
            model_name='triggeraction',
            name='action',
            field=models.CharField(choices=[('create', '创建记录'), ('update', '更新记录'), ('delete', '删除记录'), ('notify', '发送通知')], max_length=20, verbose_name='类型'),
        ),
    ]