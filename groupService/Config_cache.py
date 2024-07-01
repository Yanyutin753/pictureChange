import json
import os


class group_cache:
    _cached_data = None

    @staticmethod
    def load_from_json():
        # 从JSON文件加载数据到静态缓存
        cursor = os.path.dirname(__file__)
        config_path = os.path.join(cursor, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                group_cache._cached_data = json.load(f)
        else:
            raise FileNotFoundError(f"配置文件 {config_path} 未找到。")

    @staticmethod
    def get_cached_data():
        # 获取缓存数据
        if group_cache._cached_data:
            return group_cache._cached_data
        else:
            group_cache.load_from_json()
            return group_cache._cached_data

    @staticmethod
    def refresh_cache():
        # 强制刷新缓存数据
        group_cache.load_from_json()
