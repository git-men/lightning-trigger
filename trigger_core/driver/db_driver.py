import json
from django.db import transaction
from django.apps import apps
from django.core import serializers


from api_basebone.core import exceptions
from api_basebone.restful.serializers import multiple_create_serializer_class
from ..cache import trigger_cache, trigger_list_cache
from .. import const
from . import TriggerDriver

from .. import models
from ..models import Trigger
from ..models import TriggerAction


def queryset_to_json(queryset, expand_fields, exclude_fields):
    serializer_class = multiple_create_serializer_class(
        queryset.model, expand_fields=expand_fields, exclude_fields=exclude_fields
    )
    serializer = serializer_class(queryset, many=True)
    return serializer.data


def get_trigger_config(slug):
    config = trigger_cache.get_config(slug)
    if config:
        config = json.loads(config)
        return config
    trigger = Trigger.objects.filter(slug=slug).first()
    if not trigger:
        raise exceptions.BusinessException(
            error_code=exceptions.OBJECT_NOT_FOUND, error_data=f'找不到对应的trigger：{slug}'
        )
    expand_fields = [
        'triggeraction_set'
    ]
    exclude_fields = {
        'trigger_core__triggeraction': ['id', 'trigger'],
    }

    serializer_class = multiple_create_serializer_class(
        Trigger, expand_fields=expand_fields, exclude_fields=exclude_fields
    )
    serializer = serializer_class(trigger)
    config = serializer.data

    trigger_cache.set_config(slug, json.dumps(config))
    return config


def add_trigger(config):
    """新建触发器"""
    slug = config.get('slug')
    if not slug:
        slug = models.UUID()
        config['slug'] = slug
    api = Trigger.objects.filter(slug=slug).first()
    if api:
        raise exceptions.BusinessException(error_code=exceptions.SLUG_EXISTS)

    save_trigger(config)
    trigger_list_cache.delete_cache('trigger_list')


def update_trigger(id, config):
    """更新触发器"""
    save_trigger(config, id)


def save_trigger(config, id=None):
    """触发器配置信息保存到数据库"""
    with transaction.atomic():
        if id is None:
            slug = config.get('slug')
            if not slug:
                slug = models.UUID()
                config['slug'] = slug
            trigger = Trigger.objects.filter(slug=slug).first()
            if not trigger:
                trigger = Trigger()
                trigger.slug = slug
                is_create = True
            else:
                is_create = False
        else:
            trigger = Trigger.objects.get(id=id)
            is_create = False

        if 'name' in config:
            """如果没有就用默认值"""
            trigger.name = config['name']

        if 'description' in config:
            """如果没有就用默认值"""
            trigger.description = config['description']

        if 'disable' in config:
            """如果没有就用默认值"""
            trigger.disable = config['disable']

        trigger.event = config['event']
        if trigger.event not in const.TRIGGER_EVENTS:
            raise exceptions.BusinessException(
                error_code=exceptions.PARAMETER_FORMAT_ERROR,
                error_data=f'\'operation\': {trigger.event} 不是合法的触发器事件',
            )

        trigger.condition = config.get('condition')

        trigger.save()

       
        save_trigger_action(trigger, config.get('triggeraction'), is_create)

        trigger_cache.delete_config(trigger.slug)


# def save_trigger_condition(trigger: Trigger, condition: dict, is_create):
#     if hasattr(trigger, 'condition'):
#         condition_model = trigger.condition
#     else:
#         condition_model = TriggerCondition()
#         condition_model.trigger = trigger

#     for attr, value in condition.items():
#         if hasattr(condition_model, attr):
#             setattr(condition_model, attr, value)
#     condition_model.save()

#     try:
#         apps.get_model(condition_model.app, condition_model.model)
#     except LookupError:
#         raise exceptions.BusinessException(
#             error_code=exceptions.PARAMETER_FORMAT_ERROR,
#             error_data=f'{condition_model.app}__{condition_model.model} 不是有效的model',
#         )


def save_trigger_action(trigger: Trigger, actions, is_create):
    if not is_create:
        TriggerAction.objects.filter(trigger__id=trigger.id).delete()

    for action in actions:
        action_model = TriggerAction()
        action_model.trigger = trigger
        action_model.action = action['action']
        action_model.app = action.get('app', '')
        action_model.model = action.get('model', '')
        action_model.script = action.get('script', '')
        if action_model.action not in const.TRIGGER_ACTIONS:
            raise exceptions.BusinessException(
                error_code=exceptions.PARAMETER_FORMAT_ERROR,
                error_data=f'\'operation\': {action_model.action} 不是合法的触发器行为',
            )

        if 'fields' in action:
            action_model.fields = action['fields']

        if 'filters' in action:
            action_model.filters = action['filters']

        action_model.save()

def check_kwargs(kwargs, condition):
    ty = True
    for key in kwargs.keys():
        if kwargs.get(key, None) != condition.get(key, None):
            ty = False
            return
    return ty

def list_trigger():
    trigger_list = []
    cache_trigger_list = trigger_list_cache.get_cache('trigger_list')
    if cache_trigger_list is None:
        ls = []
        for trg in Trigger.objects.values('event','slug').all():
            ls.append(trg)
        trigger_list = ls
        trigger_list_cache.set_cache('trigger_list',json.dumps(trigger_list))
    else:
        trigger_list = json.loads(cache_trigger_list)
    return trigger_list


class DBDriver(TriggerDriver):
    def get_trigger_config(self, slug):
        return get_trigger_config(slug)

    def list_trigger_config(self, event=None, *args, **kwargs):
        triggers = list_trigger()
        results = []
        for trg in triggers:
            r = get_trigger_config(trg['slug'])
            if not(r["event"] != event) and check_kwargs(kwargs, r["condition"]):        
                results.append(r)
        return results

    def add_trigger(self, config):
        add_trigger(config)

    def update_trigger(self, id, config):
        update_trigger(id, config)

    def save_trigger(self, config, id=None):
        save_trigger(config, id)


driver = DBDriver()
