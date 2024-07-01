import os
import json


class Group_cache:
    _cached_data = None  # 静态变量用于存储缓存数据

    def __init__(self):
        Group_cache.load_from_json()

    @staticmethod
    def load_from_json():
        # 从JSON文件加载数据到静态缓存
        cursor = os.path.dirname(__file__)
        config_path = os.path.join(cursor, "Group.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                Group_cache._cached_data = json.load(f)
        else:
            raise FileNotFoundError(f"配置文件 {config_path} 未找到。")

    @staticmethod
    def get_cached_data():
        # 获取缓存数据
        if Group_cache._cached_data:
            return Group_cache._cached_data
        else:
            return None

    @staticmethod
    def refresh_cache():
        # 强制刷新缓存数据
        Group_cache.load_from_json()

