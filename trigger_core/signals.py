from django.dispatch import receiver

from api_core.api.views import ApiViewSet

from . import const
from .services import trigger_services

from api_core.signals import bsm_before_create
from api_core.signals import bsm_after_create
from api_core.signals import bsm_before_update
from api_core.signals import bsm_after_update
from api_core.signals import bsm_before_delete
from api_core.signals import bsm_after_delete

from api_basebone.signals import post_bsm_create, post_bsm_delete


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

@receiver(bsm_before_create, sender=ApiViewSet, dispatch_uid='before_create')
def handle_before_create(sender, apiViewSet, new_inst, **kwargs):
    api = apiViewSet.api
    trigger_services.handle_triggers(
        apiViewSet.request,
        const.TRIGGER_EVENT_BEFORE_CREATE,
        id=new_inst.id,
        old_inst=None,
        new_inst=new_inst,
        app=api.app,
        model=api.model,
    )


@receiver(bsm_after_create, sender=ApiViewSet, dispatch_uid='after_create')
def handle_after_create(sender, apiViewSet, new_inst, **kwargs):
    api = apiViewSet.api
    trigger_services.handle_triggers(
        apiViewSet.request,
        const.TRIGGER_EVENT_AFTER_CREATE,
        id=new_inst.id,
        old_inst=None,
        new_inst=new_inst,
        app=api.app,
        model=api.model,
    )


@receiver(bsm_before_update, sender=ApiViewSet, dispatch_uid='before_update')
def handle_before_update(sender, apiViewSet, old_inst, new_inst, **kwargs):
    api = apiViewSet.api
    trigger_services.handle_triggers(
        apiViewSet.request,
        const.TRIGGER_EVENT_BEFORE_UPDATE,
        id=new_inst.id,
        old_inst=old_inst,
        new_inst=new_inst,
        app=api.app,
        model=api.model,
    )


@receiver(bsm_after_update, sender=ApiViewSet, dispatch_uid='after_update')
def handle_after_update(sender, apiViewSet, old_inst, new_inst, **kwargs):
    api = apiViewSet.api
    trigger_services.handle_triggers(
        apiViewSet.request,
        const.TRIGGER_EVENT_AFTER_UPDATE,
        id=new_inst.id,
        old_inst=old_inst,
        new_inst=new_inst,
        app=api.app,
        model=api.model,
    )


@receiver(bsm_before_delete, sender=ApiViewSet, dispatch_uid='before_delete')
def handle_before_delete(sender, apiViewSet, old_inst, **kwargs):
    api = apiViewSet.api
    trigger_services.handle_triggers(
        apiViewSet.request,
        const.TRIGGER_EVENT_BEFORE_DELETE,
        id=old_inst.id,
        old_inst=old_inst,
        new_inst=None,
        app=api.app,
        model=api.model,
    )


@receiver(bsm_after_delete, sender=ApiViewSet, dispatch_uid='after_delete')
def handle_after_delete(sender, apiViewSet, old_inst, **kwargs):
    api = apiViewSet.api
    trigger_services.handle_triggers(
        apiViewSet.request,
        const.TRIGGER_EVENT_AFTER_DELETE,
        id=old_inst.id,
        old_inst=old_inst,
        new_inst=None,
        app=api.app,
        model=api.model,
    )
