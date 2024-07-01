# 此类用于存放音乐回复处理操作
import json
import os
import re
import time
import urllib
import requests
from bot import bot_factory
from bridge.bridge import Bridge
from common.log import logger
from plugins import EventAction
from plugins.pictureChange.message import message_reply


def music_prompt(bot_prompt, prompt, e_context):
    """
    用于生成音乐提示
    :param bot_prompt: 机器人提示
    :param prompt: 用户提示
    :param e_context: 会话消息
    :return: 生成的音乐提示
    """
    try:
        context = e_context['context']
        session_id = context.content.strip()
        bot = bot_factory.create_bot(Bridge().btype['chat'])
        session = bot.sessions.build_session(session_id, bot_prompt)
        session.add_query(prompt)
        result = bot.reply_text(session)
        return str(result.get("content"))
    except Exception:
        # logger.error("music_handle: music prompt error")
        return prompt


class music_handle:
    def __init__(self):
        super().__init__()

    # 用于将文本转换为音乐
    @staticmethod
    def text_to_music(bot_prompt, is_use_gpt, url, key, prompt, model, is_wecom, e_context):
        """
        用于将文本转换为音乐
        :param bot_prompt: 机器人提示
        :param is_use_gpt: 是否使用GPT（是：文生音；否：图生音）
        :param url: 请求的URL
        :param key: 授权Key
        :param prompt: 用户提示
        :param model: 模型
        :param is_wecom: 是否为企业微信
        :param e_context: 上下文
        :return: None
                """
        if is_use_gpt:
            prompt = music_prompt(bot_prompt, prompt, e_context)

        # 设置请求头
        headers = {
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        # 设置请求体
        payload = {
            "model": model,
            "stream": True,
            "messages": [
                {
                    "content": str(prompt),
                    "role": "user"
                }
            ]
        }

        # 初始化音乐相关变量，包括歌名、类型、完整歌词、歌曲图片、临时链接、歌曲、视频
        song_name = ""
        genre = ""
        full_lyrics = ""
        song_image = ""
        music_link1 = ""
        music_link2 = ""
        song1 = ""
        video1 = ""

        # 初始化布尔标识
        song_info_printed = False
        lyrics_image_printed = False
        music_links_printed = False
        songs_printed = False
        videos_printed = False

        try:
            # 发送请求并处理响应
            with requests.post(url, headers=headers, json=payload, stream=True) as response:
                response.raise_for_status()
                for i, line in enumerate(response.iter_lines()):
                    line = line.decode('utf-8')
                    if line.startswith("data:") and "[DONE]" not in line:
                        try:
                            # 将UTF-8字符串重新编码为GBK并处理可能的编码错误
                            line_gbk = line.replace("data: ", "")
                            json_data = json.loads(line_gbk)
                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                delta = json_data['choices'][0].get('delta', {})
                                message_content = delta.get('content', "")
                                # 处理生成音乐提示的不同部分
                                if "违规" in message_content:
                                    replyText = (f"⚠️⚠️ 违规 ⚠️⚠️\n\n🤖歌曲提示\n\n{prompt}\n\n"
                                                 f"🚨注意\n\n😭您的提示词中存在违规词，歌曲创作失败😭"
                                                 f"\n\n🤗请更换提示词，我会为您重新创作✨")
                                    message_reply.tem_reply_Text_Message(replyText, e_context)
                                    break
                                if "ID" in message_content:
                                    replyText = "🤩音乐已经生成，敬请期待！\n✨温馨提示：用英文表述音乐术语，结果会更准确哟~"
                                    message_reply.tem_reply_Text_Message(replyText, e_context)
                                if "歌名" in message_content:
                                    song_name_match = re.search(r'歌名\*\*：(.+?)\n', message_content)
                                    if song_name_match:
                                        song_name = song_name_match.group(1).strip()
                                elif "类型" in message_content:
                                    genre_match = re.search(r'类型\*\*：(.+)', message_content)
                                    if genre_match:
                                        genre = genre_match.group(1).strip()
                                elif "完整歌词" in message_content:
                                    lyrics_match = re.search(r'```\n(.+?)\n```', message_content, re.DOTALL)
                                    if lyrics_match:
                                        full_lyrics = lyrics_match.group(1).strip()
                                elif "image_large_url" in message_content:
                                    url_match = re.search(r'https?://.*?\)', message_content)
                                    if url_match:
                                        song_image = url_match.group(0).rstrip(')')
                                elif "实时音乐" in message_content:
                                    music_links = re.findall(r'https?://\S+', message_content)
                                    if music_link1:
                                        music_link2 = music_links[0]
                                    if len(music_links) > 0 and not music_link1:
                                        music_link1 = music_links[0]
                                elif "CDN" in message_content and "音乐" in message_content:
                                    url_matches = re.findall(r'https?://\S+\.mp3', message_content)
                                    for idx, match in enumerate(url_matches):
                                        if idx == 0:
                                            song1 = match
                                        elif idx == 1:
                                            song2 = match
                                elif "视频链接" in message_content:
                                    url_matches = re.findall(r'https?://\S+\.mp4', message_content)
                                    for idx, match in enumerate(url_matches):
                                        if idx == 0:
                                            video1 = match
                                        elif idx == 1:
                                            video2 = match

                                if is_wecom:
                                    # 处理企业微信消息
                                    if song_name and genre and full_lyrics and not song_info_printed:
                                        replyText = f"⭐⭐ 歌曲信息 ⭐⭐\n\n『歌名』\n{song_name}\n\n『类型』\n{genre}\n\n『完整歌词』\n{full_lyrics}"
                                        message_reply.tem_reply_Text_Message(replyText, e_context)

                                        song_info_printed = True
                                    if song_image and not lyrics_image_printed:
                                        message_reply.tem_reply_Image_Url_Message(song_image, e_context)
                                        lyrics_image_printed = True
                                    if music_link1 and music_link2 and not music_links_printed:
                                        replyText = (
                                            f"🎵🎵 即刻体验 🎵🎵\n\n『实时音乐1️⃣』\n{music_link1}\n\n『实时音乐2️⃣』\n{music_link2}\n\n"
                                            f"🚀音乐MP3和视频正在火速生成中，大概需要2-3分钟，请耐心等待！")
                                        message_reply.tem_reply_Text_Message(replyText, e_context)
                                        music_links_printed = True
                                    if song1 and song2 and not songs_printed:
                                        replyText = f"🎧🎧 音乐 🎧🎧\n\n{song1}"
                                        message_reply.tem_reply_Text_Message(replyText, e_context)
                                        songs_printed = True
                                    if video1 and video2 and not videos_printed:
                                        replyText = f"📽📽 视频 📽📽\n\n{video1}"
                                        message_reply.tem_reply_Text_Message(replyText, e_context)
                                        videos_printed = True
                                else:
                                    # 处理普通消息
                                    # 同时回复歌名、类型和完整歌词
                                    if song_name and genre and full_lyrics and not song_info_printed:
                                        replyText = f"⭐⭐ 歌曲信息 ⭐⭐\n\n『歌名』\n{song_name}\n\n『类型』\n{genre}\n\n『完整歌词』\n{full_lyrics}"
                                        message_reply.tem_reply_Text_Message(replyText, e_context)
                                        song_info_printed = True
                                    # 回复歌曲图片
                                    if song_image and not lyrics_image_printed:
                                        message_reply.tem_reply_Image_Url_Message(song_image, e_context)
                                        lyrics_image_printed = True
                                    # 回复实时音乐链接
                                    if music_link1 and music_link2 and not music_links_printed:
                                        replyText = (
                                            f"🎵🎵 即刻体验 🎵🎵\n\n『实时音乐1️⃣』\n{music_link1}\n\n『实时音乐2️⃣』\n{music_link2}\n\n"
                                            f"🚀音乐MP3和视频正在火速生成中，大概需要2-3分钟，请耐心等待！")
                                        message_reply.tem_reply_Text_Message(replyText, e_context)
                                        music_links_printed = True
                                    # 回复歌曲
                                    if song1 and song2 and not songs_printed:
                                        while requests.get(song1).status_code != 200:
                                            time.sleep(1)
                                        # 生成唯一的文件名
                                        query = "music_" + str(int(time.time()))
                                        file_name1 = f"{query}.mp3"
                                        file_path1 = os.path.join("tmp", file_name1)
                                        # 确保 tmp 目录存在
                                        if not os.path.exists("tmp"):
                                            os.makedirs("tmp")
                                        try:
                                            with urllib.request.urlopen(song1) as response1, open(file_path1,
                                                                                                  'wb') as out_file1:
                                                out_file1.write(response1.read())
                                            logger.info(f"[singsong]Music {file_path1} 下载成功, {song1}")
                                            message_reply.tem_reply_Video_Message(file_path1, e_context)
                                            songs_printed = True
                                        except Exception as e:
                                            continue
                                            logger.error(f"Error downloading song: {e}")
                                    # 回复视频
                                    if video1 and video2 and not videos_printed:
                                        while requests.get(video1).status_code != 200:
                                            time.sleep(1)
                                        logger.info(f"{video1}")
                                        message_reply.reply_Video_Url_Message(True, video1, e_context)
                                        videos_printed = True
                                        break
                        except Exception:
                            continue

                    elif "[DONE]" in line:
                        break

                    else:
                        continue

        except Exception as e:
            message_reply.reply_Error_Message(f"music_handle: {e}")
            raise Exception(f"An error occurred: {e}")
        finally:
            e_context.action = EventAction.BREAK_PASS
