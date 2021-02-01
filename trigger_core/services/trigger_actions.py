import logging
import smtplib
import hashlib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from django.apps import apps
from django.contrib.auth import get_user_model

from api_basebone.services.expresstion import resolve_expression
from api_basebone.utils import queryset as queryset_util
from bsm_config.settings import site_setting
from bsm_config.settings import site_setting

from trigger_core.services.script_action import  lightning_rt_trigger_scripts


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


@reg_action
def script(conf, variables):
    """执行脚本
    """
    # 找到脚本
    slug = conf['slug']
    script = conf.get('script', None)
    if not script:
        return
    check_sum = hashlib.md5(script.encode('utf-8')).hexdigest()
    script_name = f'{slug}_{check_sum}'
    func = getattr(lightning_rt_trigger_scripts, script_name, None)
    if not func:
        func_name = f'trigger_action_{slug}'
        head = f'def {func_name}(context):'
        body = ('\n' + script.strip()).replace('\n', '\n' + ' ' * 4).replace('\t', ' ' * 4)
        print(head + body)
        exec(head + body)
        func = locals().get(func_name, None)
        if not func:
            print('can not create function from script')
            return
        
        # 先清理旧版本的模块方法
        old_func = [f for f in dir(lightning_rt_trigger_scripts) if f.startswith(slug)]
        for of in old_func:
            delattr(lightning_rt_trigger_scripts, of)
        
        # 把新版本的方法植入
        setattr(lightning_rt_trigger_scripts, script_name, func)

    # 执行脚本 
    try:
        context = variables
        if isinstance(variables, Variable):
            context = variables.__dict__
        return func(context)
    except:
        # TODO 执行可以有更多的选项，例如是否影响务事等。
        raise


class Variable:
    def __init__(self, id=None, old=None, new=None, user=None):
        self.id = id
        self.old = old
        self.new = new
        self.user = user
        # 可使用配置staff的user作为user
        staff_model, staff_username = site_setting['staff_model', 'staff_username']
        if staff_model and staff_username:
            StaffModel = apps.get_model(staff_model.replace('__', '.', 1))
            _user = StaffModel.objects.filter(**{staff_username: user.username}).first()
            if _user:
                self.user = _user


def run_action(conf, **kwargs):
    ACTIONS[conf.pop('action')](conf, Variable(**kwargs))
    # 不复制直接pop有隐患，当conf为缓存的配置数据的时候，会导致缓存数据的改变。
