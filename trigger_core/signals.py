from django.dispatch import receiver

from api_core.api.views import ApiViewSet

from . import const
from .services import trigger_services

from api_basebone.signals import post_bsm_create, post_bsm_delete, before_bsm_create, before_bsm_delete


@receiver(post_bsm_create, dispatch_uid='post_bsm_create_by_trigger')
def handler_post_bsm_create(sender, instance, create, request, old_instance, **kwargs):
    """数据保存后
    """
    print('数据保存后啦！')
    trigger_services.handle_triggers(
        request,
        const.TRIGGER_EVENT_AFTER_CREATE if create else const.TRIGGER_EVENT_AFTER_UPDATE,
        id=instance.pk,
        old_inst=old_instance,
        new_inst=instance,
        app=sender._meta.app_label,
        model=sender._meta.model_name,
    )

@receiver(post_bsm_delete, dispatch_uid='post_bsm_delete_by_trigger')
def handler_post_bsm_delete(sender, instance, request, **kwargs):
    trigger_services.handle_triggers(
        request,
        const.TRIGGER_EVENT_AFTER_DELETE,
        id=instance.pk,
        old_inst=instance,
        new_inst=None,
        app=sender._meta.app_label,
        model=sender._meta.model_name,
    )


@receiver(before_bsm_create, dispatch_uid='before_bsm_create_by_trigger')
def handle_before_create(sender, instance, create, request, **kwargs):
    trigger_services.handle_triggers(
        request,
        const.TRIGGER_EVENT_BEFORE_CREATE if create else const.TRIGGER_EVENT_BEFORE_UPDATE,
        id=None if create else instance['id'],
        old_inst=None,
        new_inst=instance,
        app=sender._meta.app_label,
        model=sender._meta.model_name
    )

@receiver(before_bsm_delete, dispatch_uid='before_bsm_delete_by_trigger')
def handle_before_delete(sender, instance, request, **kwargs):
    trigger_services.handle_triggers(
        request,
        const.TRIGGER_EVENT_BEFORE_DELETE,
        id=instance.pk,
        old_inst=instance,
        new_inst=None,
        app=sender._meta.app_label,
        model=sender._meta.model_name
    )
