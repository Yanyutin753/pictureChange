
import os
import json
from plugins.pictureChange.groupService.Config_cache import Group_cache
from common.log import logger


class find_group:
    @staticmethod
    def find_group(group_name):
        all_conf = Group_cache().get_cached_data()  # 从缓存获取内容
        # 获取群聊名称，要放到插件，将上面改成def find_group(self, e_context: EventContext)，去掉下行注释
        # group_name = e_context["msg"].other_user_nickname
        if all_conf is None:
            logger.info("缓存内容不存在")

        if all_conf['group']:
            for group in all_conf["group"]:
                if group_name == group["name"]:
                    funct_dic = group["function"]
                    funct_values = list(funct_dic.values())
                    funct_keys = list(funct_dic.keys())
                    values = list(all_conf["AllFunction"].values())
                    keys = list(all_conf["AllFunction"].keys())
                    ans_dic = {}
                    for i in range(len(keys)):
                        if i == len(keys) - 1:  # 保证最后一个列表项为model即可
                            if funct_values[i] in values[i]:
                                ans_dic[funct_keys[i]] = funct_values[i]
                                continue
                        if values[i] == "True" and values[i] == funct_values[i]:
                            ans_dic[funct_keys[i]] = "True"
                        else:
                            ans_dic[funct_keys[i]] = "False"

                    return ans_dic
            else:
                return None
        else:
            return None
