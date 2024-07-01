import json
import re
import threading

from common.log import logger
from plugins.pictureChange.groupService.find_group import find_group
from plugins.pictureChange.groupService.Config_cache import Group_cache

"""

"""


class GroupConfig:
    def __init__(self, config_file='group.json'):
        self.config = None
        self.config_file = config_file
        self.mode = None
        self.load_config()
        self.lock = threading.Lock()  # 初始化线程锁

    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            self.config = {
                "AllFunction": {
                    "IS_IMAGE": "True",
                    "IS_FILE": "True",
                    "IS_MUSIC": "True",
                    "MODEL": ["GPT3-5", "GLM-4"]
                },
                "group": []
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(self.config, file, ensure_ascii=False, indent=4)

    def ins_command(self, ins):
        with self.lock:  # 使用线程锁确保同一时间只有一个线程访问
            reply = ""
            if ins == "#help":
                self.mode = "help"
                return ("修改总功能，请使用#change [funct] to [state]来修改总功能\n"
                        "修改已有群聊功能模式，请使用#change [funct] in [group_name] to [state]来修改群聊功能状态\n新增群聊模式，请使用#add ["
                        "group_name]来新增群聊"
                        "\n删除群聊模式，请使用#del [group_name]来删除群聊\n"
                        "修改群聊模型模式，请使用#change [group_name] to [model]来修改模型")
            if ins[:7] == "#change":
                self.mode = "modify_group_function"
                reply = self.change_command(ins)
            elif ins[:13] == "#change Model":
                self.mode = "modify_group_model"
                reply = self.change_command(ins)
            elif ins[:4] == "#add":
                self.mode = "add_group"
                reply = self.add_command(ins)
            elif ins[:4] == "#del":
                self.mode = "del_group"
                reply = self.del_command(ins)
            elif ins[:7] == "#modify":
                self.mode = "modify_group_model"
                reply = self.change_command(ins)
            else:
                self.mode = None
                reply = f"未知指令 {ins}"
            Group_cache.load_from_json()
            logger.info("已将更新数据放入缓存")
            return reply

    def change_command(self, command):
        def normalize_state(state):
            return state.capitalize()

        change_pattern = re.compile(r'^#modify (\w+) to (\w+)$')
        group_change_pattern = re.compile(r'^#change (\w+) in (.+) to (\w+)$')
        model_change_pattern = re.compile(r'#modify (.+?) to (.+)')
        if self.mode == "all_function":
            change_match = change_pattern.match(command)
            if change_match:
                funct, state = change_match.groups()
                funct = funct.upper()
                state = normalize_state(state)
                if funct in (key.upper() for key in self.config["AllFunction"]):
                    self.config["AllFunction"][funct] = state
                    self.save_config()
                    return f"功能 {funct} 已修改为 {state}"
                else:
                    return f"功能 {funct} 不存在于 AllFunction 中"
            else:
                return f"未知指令 {command}"

        elif self.mode == "modify_group_function":
            group_change_match = group_change_pattern.match(command)
            if group_change_match:
                funct, group_name, state = group_change_match.groups()
                funct = funct.upper()
                state = normalize_state(state)
                if funct == "MODEL":
                    return "您没有对应权限"
                group_found = False
                for group in self.config["group"]:
                    if group["name"] == group_name:
                        group_found = True
                        if funct in (key.upper() for key in group["function"]):
                            group["function"][funct] = state
                            self.save_config()
                            return f"群聊 {group_name} 的功能 {funct} 已修改为 {state}"
                        else:
                            return f"功能 {funct} 不存在于群聊 {group_name} 中"
                if not group_found:
                    return f"没有找到对应群聊 {group_name}"
            else:
                return f"未知指令 {command}"

        elif self.mode == "modify_group_model":
            model_change_match = model_change_pattern.match(command)
            if model_change_match:
                group_name, model = model_change_match.groups()
                model = model.upper()
                group_found = False
                for group in self.config["group"]:
                    if group["name"] == group_name:
                        group_found = True
                        if model in (m.upper() for m in self.config["AllFunction"]["MODEL"]):
                            group["function"]["MODEL"] = model
                            self.save_config()
                            return f"群聊 {group_name} 的模型已修改为 {model}"
                        else:
                            return f"模型 {model} 不存在于可用模型列表中"
                if not group_found:
                    return f"没有找到对应群聊 {group_name}"
            else:
                return f"未知指令 {command}"
        else:
            return f"当前模式不支持此指令 {command}"

    def add_command(self, command):
        add_pattern = re.compile(r'^#add (.+)$')
        add_match = add_pattern.match(command)
        if add_match:
            group_name = add_match.group(1)
            for group in self.config["group"]:
                if group["name"] == group_name:
                    return f"群聊名 {group_name} 已经被使用"
            new_group = {
                "name": group_name,
                "function": {
                    "IMAGE": "False",
                    "FILE": "False",
                    "MUSIC": "False",
                    "ENABLE": "True",
                    "MODEL": "GPT_4",
                }
            }
            self.config["group"].append(new_group)
            self.save_config()
            return f"群聊 {group_name} 已成功新增"
        else:
            return f"未知指令 {command}"

    def del_command(self, command):
        del_pattern = re.compile(r'^#del (.+)$')
        del_match = del_pattern.match(command)
        if del_match:
            group_name = del_match.group(1)
            group_found = False
            for group in self.config["group"]:
                if group["name"] == group_name:
                    group_found = True
                    self.config["group"].remove(group)
                    self.save_config()
                    return f"群聊 {group_name} 已成功删除"
            if not group_found:
                return f"没有找到对应群聊 {group_name}"
        else:
            return f"未知指令 {command}"


# 测试代码
manager = GroupConfig()
print(manager.ins_command("#modify 500 Not Found to abab6.5s-chat"))
# print(manager.ins_command("#add 505_b"))
# print(manager.ins_command("#del 500 Not Found"))
# print(Group_cache.get_cached_data())
# findGroup = find_group()
# s = findGroup.find_group("505_b")
# print(s)
# print(manager.ins_command("#modify is_music to false"))
# print(manager.ins_command("#modify is_file to true"))
