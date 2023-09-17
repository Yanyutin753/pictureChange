import os
import json

curdir = os.path.dirname(__file__)
# 拿到上两级的文件
config_path = os.path.join(curdir, "../../config.json")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        channel_type = config["channel_type"]

        if channel_type == "wechatcom_app" or channel_type == "wechatmp" or channel_type == "wechatmp_service":
            from .pictureChange_app import *
        elif channel_type == "wx":
            from .pictureChange_wx import *
        else:
            # 处理未知的 channel_type 值
            raise ValueError("Unknown channel_type: {}".format(channel_type))
except FileNotFoundError:
    # 处理找不到配置文件的情况
    raise FileNotFoundError("Config file not found: {}".format(config_path))
