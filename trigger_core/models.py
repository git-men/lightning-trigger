import logging
import uuid

from api_basebone.export.specs import FieldType
from . import const

from django.db import models
from django.conf import settings
from api_basebone.core.fields import JSONField

logger = logging.getLogger('django')


def UUID():
    return uuid.uuid4().hex


class Trigger(models.Model):
    '''触发器'''

    slug = models.SlugField('标识', max_length=50, unique=True, default=UUID)
    name = models.CharField('名称', max_length=50, default='')
    description = models.CharField('说明', max_length=1024, default='')
    event = models.CharField('操作', max_length=20, choices=const.TRIGGER_EVENT_CHOICES)
    disable = models.BooleanField('停用', default=False)
    condition = JSONField('触发条件',default={})
    create_time = models.DateTimeField('创建时间', auto_now_add=True, null=True)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, verbose_name='创建人', null=True)

    def __str__(self):
        return '%s object (%s,%s,%s)' % (
            self.__class__.__name__,
            self.pk,
            self.slug,
            self.event,
        )

    class Meta:
        verbose_name = '触发器'
        verbose_name_plural = '触发器'

    class GMeta:
        creator_field = 'create_by'
        annotated_fields = {
            'enable': {
                'display_name': '启用',
                'type': FieldType.BOOL,
                'annotation': models.Case(
                    models.When(disable=False, then=models.Value(True)),
                    models.When(disable=True, then=models.Value(False)),
                    output_field=models.CharField(),
                ),
            }
        }

"""
class TriggerCondition(models.Model):
    # 触发器条件

    trigger = models.OneToOneField(
        Trigger, models.CASCADE, verbose_name='trigger_condition'
    )
    app = models.CharField('app名字', max_length=50, null=True)
    model = models.CharField('数据模型名字', max_length=50, null=True)
    filters = JSONField('筛选条件', default=[], blank=True)

    def __str__(self):
        return '%s object (%s,%s,%s)' % (
            self.__class__.__name__,
            self.pk,
            self.app,
            self.model,
        )

    class Meta:
        verbose_name = '触发器条件'
        verbose_name_plural = '触发器条件'

        index_together = [('app', 'model')]
"""

ACTION_TYPE_RECORD = 'record'
ACTION_TYPE_NOTIFY = 'notify'
ACTION_TYPE_SCRIPT = 'script'
ACTION_TYPE_API = 'api'

ACTION_TYPES = (
    (ACTION_TYPE_RECORD, '数据操作'),
    (ACTION_TYPE_NOTIFY, '发送通知'),
    (ACTION_TYPE_SCRIPT, '执行脚本'),
    (ACTION_TYPE_API, '调用接口')
)

class TriggerAction(models.Model):
    """触发器行为"""

    MIME_TYPE_PLAIN = 'plain'
    MIME_TYPE_HTML = 'html'

    slug = models.SlugField('标识', max_length=50, unique=True, default=UUID)
    trigger = models.ForeignKey(Trigger, models.CASCADE, verbose_name='trigger')
    action = models.CharField('响应', max_length=20, choices=const.TRIGGER_ACTION_CHOICES)
    # action_type = models.CharField('响应类型', max_length=50, default=ACTION_TYPE_RECORD)
    description = models.CharField('描述', max_length=140, blank=True, null=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True, null=True)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, verbose_name='创建人', null=True)

    app = models.CharField('app名称', default='', max_length=50)
    model = models.CharField('模型名称', default='', max_length=50)
    fields = JSONField('操作的属性', default={}, blank=True)
    filters = JSONField('操作的条件', default=[], blank=True)

    title_template = models.CharField('标题模板', max_length=100, default='')
    content_template = models.TextField('正文模板', default='')
    receiver_filters = JSONField('接收者的过滤条件', default=[], blank=True)
    
    email_enabled = models.BooleanField('启用邮件通知', default=False)
    email_mime_type = models.CharField('格式', max_length=20, choices=[[MIME_TYPE_PLAIN, '纯文本'], [MIME_TYPE_HTML, '富文本']], default=MIME_TYPE_PLAIN)
    
    script = models.TextField('脚本', null=True)
    
    class Meta:
        verbose_name = '触发动作'
        verbose_name_plural = '触发动作'
    
    class GMeta:
        creator_field = 'create_by'

# class RecordAction(TriggerAction):
#     app = models.CharField('app名称', default='', max_length=50)
#     model = models.CharField('模型名称', default='', max_length=50)
#     fields = JSONField('操作的属性', default={}, blank=True)
#     filters = JSONField('操作的条件', default=[], blank=True)

#     class Meta:
#         verbose_name = '数据操作'
#         verbose_name_plural = '数据操作'


# class NotifyAction(TriggerAction):
#     MIME_TYPE_PLAIN = 'plain'
#     MIME_TYPE_HTML = 'html'

#     title_template = models.CharField('标题模板', max_length=100, default='')
#     content_template = models.TextField('正文模板', default='')
#     receiver_filters = JSONField('接收者的过滤条件', default=[], blank=True)
    
#     email_enabled = models.BooleanField('启用邮件通知', default=False)
#     email_mime_type = models.CharField('格式', max_length=20, choices=[[MIME_TYPE_PLAIN, '纯文本'], [MIME_TYPE_HTML, '富文本']], default=MIME_TYPE_PLAIN)
    
#     class Meta:
#         verbose_name = '发送通知'
#         verbose_name_plural = '发送通知'


# class ScriptAction(TriggerAction):
#     """调用脚本动作
#     """
#     script = models.TextField('脚本')

#     class Meta:
#         verbose_name = '执行脚本'
#         verbose_name_plural = '执行脚本'
