import json
import os
import random
import string

from common.log import logger


class adminService:
    def __init__(self):
        # 存储的管理员及激活码
        self.admin_id = []
        self.admin_password = []
        # 读取配置文件
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.admin_id = config["admin_id"]
            self.admin_password = config["admin_password"]
            if self.admin_password == "":
                # 生成随机密码
                self.admin_password = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            logger.info(f"[adminService] 读取配置文件成功! admin_id: {self.admin_id}, admin_password: {self.admin_password}")

    # 认证管理员,然后写入config中
    def verify_admin(self, user_id: str, admin_password: str) -> bool:
        if admin_password != self.admin_password:
            return False
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.admin_id.append(user_id)
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            config["admin_id"].append(user_id)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True

    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admin_id

    # 修改管理员密码
    def update_password(self, user_id: str, admin_password: str) -> bool:
        if not self.is_admin(user_id):
            logger.info("False!")
            return False
        self.admin_password = admin_password
        # 保存配置文件, 修改配置文件为新密码
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            config["admin_password"] = admin_password
            logger.info(admin_password)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        logger.info(f"[adminService] 修改管理员密码成功! admin_password: {self.admin_password}")
        return True

    # 清空现有的管理员名单
    def clear_admin(self, user_id: str) -> bool:
        if not self.is_admin(user_id):
            return False
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            config["admin_id"] = []
            config["admin_id"].append(user_id)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        logger.info(f"[adminService] 清空管理员成功!")
        return True

    # 修改插件目录下的json文件，不定参数代表传递几层，如config["start"]["host"]
    def update_json(self, user_id: str, target: str, *args, value: str) -> bool:
        if not self.is_admin(user_id):
            return False
        
        # 设定文件路径
        config_path = os.path.join(os.path.dirname(__file__), "../config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            # 使用递归函数设置值
            def set_nested_value(d, keys, value):

                if len(keys) == 1:
                    d[keys[0]] = value
                else:
                    if keys[0] not in d:
                        d[keys[0]] = {}
                    set_nested_value(d[keys[0]], keys[1:], value)

            if value.isdigit():  # 判断是否是数字
                value = int(value)
            elif value.lower() == "true":  # 判断是否是布尔类型 true
                value = True
            elif value.lower() == "false":  # 判断是否是布尔类型 false
                value = False
            # 调用递归函数
            set_nested_value(config, [target] + list(args), value)
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                
            logger.info(f"[adminService] 修改json成功! target: {target}, value: {value}")
            return True
        except Exception as e:
            logger.info(f"[adminService] 修改json失败! target: {target}, value: {value}, error: {str(e)}")
            return False

    # 添加元素
    def append_json(self, user_id: str, target: str, *args, value: str) -> bool:
        if not self.is_admin(user_id):
            return False
        
        # 设定文件路径
        config_path = os.path.join(os.path.dirname(__file__), "../config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            # 使用递归函数设置值
            def set_nested_value(d, keys, value):
                if len(keys) == 1:
                    d[keys[0]].append(value)
                else:
                    if keys[0] not in d:
                        d[keys[0]] = []
                    set_nested_value(d[keys[0]], keys[1:], value)
            
            # 调用递归函数
            set_nested_value(config, [target] + list(args), value)
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                
            logger.info(f"[adminService] 修改json成功! target: {target}, value: {value}")
            return True
        except Exception as e:
            logger.info(f"[adminService] 修改json失败! target: {target}, value: {value}, error: {str(e)}")
            return False
