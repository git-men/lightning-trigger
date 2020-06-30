from django.core.cache import cache
from django.conf import settings

class BaseCache:
    """缓存基础类"""

    def set_cache(self, key, content, pipe=None):
        key = cache.make_key(key)
        cache_time = getattr(settings, 'TRIGGER_CACHE_TIME', 1 * 60)
        cache.set(key, content, cache_time)
        
    def get_cache(self, key, pipe=None):
        key = cache.make_key(key)
        return cache.get(key)

    def delete_cache(self, key, pipe=None):
        key = cache.make_key(key)
        cache.delete(key)


class TriggerCache(BaseCache):
    TRIGGER_KEY = "trigger:slug:{}"

    def set_config(self, slug, config, pipe=None):
        """缓存trigger配置"""
        self.set_cache(self.TRIGGER_KEY.format(slug), config, pipe)

    def get_config(self, slug, pipe=None):
        """读trigger缓存"""
        return self.get_cache(self.TRIGGER_KEY.format(slug), pipe)

    def delete_config(self, slug, pipe=None):
        """清trigger缓存"""
        self.delete_cache(self.TRIGGER_KEY.format(slug), pipe)


trigger_cache = TriggerCache()
trigger_list_cache = BaseCache()
