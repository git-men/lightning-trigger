import logging
import uuid

from api_basebone.export.specs import FieldType
from . import const

from django.db import models
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


class TriggerAction(models.Model):
    """触发器行为"""

    MIME_TYPE_PLAIN = 'plain'
    MIME_TYPE_HTML = 'html'

    trigger = models.ForeignKey(Trigger, models.CASCADE, verbose_name='trigger')
    action = models.CharField('类型', max_length=20, choices=const.TRIGGER_ACTION_CHOICES)
    # 创建记录, 更新记录, 删除记录
    app = models.CharField('app名字', default='', max_length=50)
    model = models.CharField('数据模型名字', default='', max_length=50)
    fields = JSONField('操作的属性', default={}, blank=True)
    filters = JSONField('操作的条件', default=[], blank=True)
    # 消息通知
    title_template = models.CharField('标题模板', max_length=100, default='')
    content_template = models.TextField('正文模板', default='')
    receiver_filters = JSONField('接收者的过滤条件', default=[], blank=True)
    # 发送邮件
    email_enabled = models.BooleanField('启用邮件通知', default=False)
    email_mime_type = models.CharField('格式', max_length=20, choices=[[MIME_TYPE_PLAIN, '纯文本'], [MIME_TYPE_HTML, '富文本']], default=MIME_TYPE_PLAIN)

    class Meta:
        verbose_name = '触发动作'
        verbose_name_plural = '触发动作'
