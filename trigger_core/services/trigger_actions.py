import logging
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from django.apps import apps
from django.contrib.auth import get_user_model

from api_basebone.services.expresstion import resolve_expression
from api_basebone.utils import queryset as queryset_util
from bsm_config.settings import site_setting


logger = logging.getLogger('bsm-trigger')


def convert_fields(fields_config, variables):
    return {
        f: resolve_expression(exp, variables=variables)
        for f, exp in fields_config.items()
    }


ACTIONS = {}


def reg_action(func):
    ACTIONS[func.__name__] = func
    return func


@reg_action
def update(conf, variables):
    model = apps.get_model(conf['app'], conf['model'])
    fields = convert_fields(conf['fields'], variables=variables)
    queryset_util.filter(model.objects, conf['filters'], context=variables).update(
        **fields
    )


@reg_action
def create(conf, variables):
    model = apps.get_model(conf['app'], conf['model'])
    fields = convert_fields(conf['fields'], variables=variables)
    model.objects.create(**fields)


@reg_action
def delete(conf, variables):
    model = apps.get_model(conf['app'], conf['model'])
    queryset_util.filter(model.objects, conf['filters'], context=variables).delete()


@reg_action
def notify(conf, variables):
    if not conf['email_enabled']:
        return
    # 批量查找数据库
    protocol, host, port, tls, need_login, username, password, sender_address, sender_name, staff_model, staff_username, staff_email = site_setting[
        'mail_protocol', 'mail_host', 'mail_port',
        'start_tls', 'mail_need_login', 'mail_username', 'mail_password',
        'sender_address', 'sender_name', 'staff_model', 'staff_username', 'staff_email'
    ]
    # 可以使用 django.core.mail.backends.smtp.EmailBackend
    Client = {'SMTP': smtplib.SMTP, 'SMTP_SSL': smtplib.SMTP_SSL}.get(protocol, None)
    if not all([Client, host, staff_model, staff_username, staff_email]):
        logging.warning('未配置好发邮件所需的相关配置')

    client = Client(host, port or 0)

    if tls:
        client.starttls()

    if need_login is not False:  # 默认为True
        if username and password:
            client.login(username, password)

    title = conf['title_template'].format(**variables.__dict__)
    content = conf['content_template'].format(**variables.__dict__)
    msg = MIMEText(content, conf['email_mime_type'], 'utf-8')
    msg['Subject'] = title
    msg['From'] = formataddr((Header(sender_name or sender_address, 'utf-8').encode(), sender_address))
    model = apps.get_model(staff_model.replace('__', '.', 1)) if staff_model else get_user_model()
    users = queryset_util.filter(
        model.objects, conf['receiver_filters'], context=variables,
    ).values_list(staff_username, staff_email)
    print(conf['receiver_filters'], users)
    if not users.exists():
        return
    msg['To'] = ','.join(f'{name} <{addr}>' for name, addr in users)
    client.sendmail(from_addr=sender_address, to_addrs=[addr for _, addr in users], msg=msg.as_string())
    client.quit()


class Variable:
    def __init__(self, id=None, old=None, new=None, user=None):
        self.id = id
        self.old = old
        self.new = new
        self.user = user


def run_action(conf, **kwargs):
    ACTIONS[conf.pop('action')](conf, Variable(**kwargs))
    # 不复制直接pop有隐患，当conf为缓存的配置数据的时候，会导致缓存数据的改变。
