import base64
import io
import urllib.parse

import requests
from oauthlib.common import urlencoded

from common.log import logger
from plugins.pictureChange.message import message_reply as MessageReply
from plugins.pictureChange.util import file_handle as FileHandle


# 百度图片处理
def read_and_encode_image(file_content):
    try:
        with open(file_content, 'rb') as file:
            image_data = file.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
        if urlencoded:
            encoded_image = urllib.parse.quote_plus(encoded_image)
        return encoded_image
    except Exception as e:
        logger.error(f"处理文件数据时出现错误：{e}")
        return None


# 回复图片
def reply_image(base64_image_data, file_content, e_context):
    try:
        image_data = base64.b64decode(base64_image_data)
        image_storage = io.BytesIO()
        image_storage.write(image_data)
        image_storage.seek(0)
        MessageReply.reply_Image_Message(True, image_storage, e_context)
        FileHandle.delete_file(file_content)
    except Exception as e:
        logger.error(f"回复图片时出现错误：{e}")


# 获取访问令牌
def get_access_token(api_key, secret_key):
    token_url = "https://aip.baidubce.com/oauth/2.0/token"
    token_params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    try:
        response = requests.post(token_url, params=token_params)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        logger.error(f"获取访问令牌时出现错误：{e}")
        return None


# 处理图片
def process_image(encoded_image, access_token):
    process_url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/image_definition_enhance"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    payload = f"image={encoded_image}"
    # logger.debug(payload)
    try:
        response = requests.post(process_url, headers=headers, data=payload, params={"access_token": access_token})
        response.raise_for_status()
        logger.debug(response.json())
        return response.json().get('image')
    except requests.RequestException as e:
        logger.error(f"API请求失败：{e}")
        return None
