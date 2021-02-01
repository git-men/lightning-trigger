import types

"""动态模块，用来存储触发器脚本。里面是一个个function，名称结构为：
app__model__triggerslug__scriptmd5
app: 应用名
model: 模型名
triggerslug: 触发器ID
scriptmd5: 脚本代码的MD5
"""
lightning_rt_trigger_scripts = types.ModuleType("lightning_rt_trigger_scripts")


def find_script_by_slug(slug):
    """查找脚本
    """
    pass

def register_script(slug, func):
    """注册脚本，func可以是一个函数，也可能是一个代码文本。
    """
    pass

"""
故事是这样的：
一、代码版
1. 编写脚本，在Py脚本里面。
2. 注册脚本，使用app, model, slug。
3. 配置触发器时，指定脚本名。
4. 触发时，查找脚本去调用。

二、配置版
1. 在界面上编写脚本，字符串来的。保存到数据库。
2. 触发时，根据脚本生成MD5查找是否已经有缓存的函数，如果有，则调用，如果无，则execute生成，再调用。

先写代码版，再演进到配置版。配置版的md5就是代码版的slug
"""
