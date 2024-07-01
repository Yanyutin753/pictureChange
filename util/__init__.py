import requests

import plugins.pictureChange.message.request_handle as MessageHandle
from bridge.bridge import Bridge
from common import const
from common.log import logger


# 文字生成图片
def text_to_image(url: str, key: str, prompt: str, model: str, session_id: str = None):
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    payload = MessageHandle.image_message(prompt, model)
    btype = Bridge().get_bot_type("chat")
    if btype not in [const.OPEN_AI, const.CHATGPT, const.CHATGPTONAZURE, const.LINKAI]:
        return
    bot = Bridge().get_bot("chat")
    bot.sessions.session_query(prompt, session_id)

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        reply = str(response.json()["data"][0]["url"]).strip()
        # 保存聊天记录（包含群聊和个人）
        # bot.sessions.session_reply(reply, session_id)
        return reply
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return f"An error occurred: {e}"


# 文字生成音乐
def text_to_music(url: str, key: str, prompt: str, model: str, max_retries: int = 1,
                  session_id: str = None):
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }

    payload = MessageHandle.music_message(prompt, model)
    btype = Bridge().get_bot_type("chat")
    if btype not in [const.OPEN_AI, const.CHATGPT, const.CHATGPTONAZURE, const.LINKAI]:
        return
    bot = Bridge().get_bot("chat")
    bot.sessions.session_query(prompt, session_id)
    retries = 0

    while retries < max_retries:
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            reply = str(response.json()["choices"][0]["message"]["content"])
            # 1.提取歌曲信息（歌名，风格，歌词，歌曲图片）
            # 2.提取有效的url，并下载到相应MP3文件

            # 保存聊天记录（包含群聊和个人）
            # bot.sessions.session_reply(reply, session_id)
            return reply

        except requests.exceptions.RequestException:
            retries += 1

    return f"Failed to retrieve content after {max_retries} attempts due to 503 errors."


# 分析文件
def recognize_file(url: str, key: str, prompt: str, file_url: str, model: str, session_id: str = None):
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }

    payload = MessageHandle.recognize_message(prompt, file_url, model)
    btype = Bridge().get_bot_type("chat")
    if btype not in [const.OPEN_AI, const.CHATGPT, const.CHATGPTONAZURE, const.LINKAI]:
        return
    bot = Bridge().get_bot("chat")
    bot.sessions.session_query(prompt, session_id)
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        reply = str(response.json()["choices"][0]["message"]["content"])
        # 保存聊天记录（包含群聊和个人）
        # bot.sessions.session_reply(reply, session_id)
        return reply
    except requests.exceptions.RequestException as e:
        if e.response:
            logger.error(f"Response content: {e.response.text}")  # Print the response content for debugging
        return f"An error occurred: {e}"


#  分析图片
def recognize_image(url: str, key: str, prompt: str, image_url: str, model: str, session_id: str = None):
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    payload = MessageHandle.recognize_message(prompt, image_url, model)
    btype = Bridge().get_bot_type("chat")
    if btype not in [const.OPEN_AI, const.CHATGPT, const.CHATGPTONAZURE, const.LINKAI]:
        return
    bot = Bridge().get_bot("chat")
    bot.sessions.session_query(prompt, session_id)
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        reply = str(response.json()["choices"][0]["message"]["content"])
        bot.sessions.session_reply(reply, session_id)
        return reply
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return f"An error occurred: {e}"
