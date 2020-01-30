import json
import logging
import traceback
from django.conf import settings
from django.apps import apps

from django.core.management.base import BaseCommand
from ...driver.db_driver import driver

log = logging.getLogger('django')


class Command(BaseCommand):
    """输出模型配置

    只是简单的输出模型的配置，输出后的配置可进行调整和修改
    """

    def add_arguments(self, parser):
        """"""
        parser.add_argument('--app', type=str, help='导出api的app')

    def handle(self, *args, **kwargs):
        """"""
        app = kwargs.get('app')
        result = {}
        result['trigger'] = self.dump_trigger(app)
        for k, d in result.items():
            print(f'{k}导出成功')
            print(f'成功的{k}：' + str(d['success_list']))
            print(f'失败的{k}：' + str(d['error_list']))

    def dump_trigger(self, app):
        """"""
        self.stdout.write('导出 trigger 配置...')
        if app:
            export_apps = [app]
        else:
            export_apps = getattr(settings, 'TRIGGER_APPS', [])
            export_apps = list(set(export_apps))

        error_list = []
        success_list = []
        for app in export_apps:
            f = None
            try:
                app_config = apps.get_app_config(app)
                path = app_config.module.__path__[0] + '/trigger_config.json'
                trigger_list = driver.list_trigger_config(app=app)
                if not trigger_list:
                    continue
                print(f'-------------------开始导出 app：{app} 的trigger配置 ------------------')
                trigger_config_list = []
                for trigger_config in trigger_list:
                    del trigger_config['id']  # trigger配置文件不用包含id
                    trigger_config_list.append(trigger_config)

                trigger_json = json.dumps(
                    trigger_config_list, ensure_ascii=False, indent=4, sort_keys=True
                )
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(trigger_json)
                    success_list.append(app)
                print(f'------------------- 导出 trigger 配置完成 ----------------------------')
                slug_list = [trigger_config['slug'] for trigger_config in trigger_list]
                print(f'导出 trigger {app} 配置完成:{slug_list}')
            except Exception as e:
                error_list.append(app)
                print('导出 trigger 异常： {}'.format(traceback.format_exc()))

        # print(f'trigger导出成功')
        # print(f'成功的app：{success_list}')
        # print(f'失败的app：{error_list}')
        return {'success_list': success_list, 'error_list': error_list}
