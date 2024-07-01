import os
import time
import urllib.parse

import requests

import plugins.pictureChange.message.message_sd_reply as SDReply
import plugins.pictureChange.util.baidu_image as Baidu_Image
from bridge.context import ContextType
from common.log import logger
from plugins import EventAction
from plugins.pictureChange import util
from plugins.pictureChange.message import message_handle as MessageHandle
from plugins.pictureChange.message import message_reply as MessageReply
from plugins.pictureChange.message import message_type as MessageType
from plugins.pictureChange.message.music_handle import music_handle
from plugins.pictureChange.util import file_handle as FileHandle


def process_image_music_content(openai_api_base, openai_api_key, image_recognize_model, prompt, recognize_func,
                                reply_message_method, e_context):
    context = e_context['context']
    session_id = context.kwargs.get('session_id')
    file_content = context.content.strip().split()[2]
    if os.path.isfile(file_content):
        try:
            file_url = FileHandle.file_toBase64(file_content)
            reply_text = recognize_func(openai_api_base,
                                        openai_api_key, prompt, file_url,
                                        image_recognize_model, session_id)
            return reply_text
        except Exception as e:
            reply_text = str(e)
            logger.error("Processing failed: {}".format(str(e)))
            reply_message_method(True, reply_text, e_context)
            return None
    else:
        reply_text = "找不到相应的图片文件，请联系管理员！"
        reply_message_method(True, reply_text, e_context)
        return None


# 描述图片信息
def process_image_content(openai_api_base, openai_api_key, image_recognize_model, prompt, recognize_func,
                          error_message, reply_message_method, e_context):
    context = e_context['context']
    session_id = context.kwargs.get('session_id')
    file_content = context.content.strip().split()[2]
    if os.path.isfile(file_content):
        try:
            file_url = FileHandle.file_toBase64(file_content)
            replyText = recognize_func(openai_api_base + "/chat/completions",
                                       openai_api_key, prompt, file_url,
                                       image_recognize_model, session_id)
        except Exception as e:
            replyText = error_message
            logger.error("Processing failed: {}".format(str(e)))
    else:
        replyText = error_message
    reply_message_method(True, replyText, e_context)


# 描述文件信息
def process_file_content(openai_api_base, openai_api_key, file_recognize_model, prompt, recognize_func,
                         error_message,
                         reply_message_method,
                         e_context):
    context = e_context['context']
    session_id = context.kwargs.get('session_id')
    file_content = context.content.strip()
    if os.path.isfile(file_content):
        try:
            file_url = FileHandle.file_toBase64(file_content)
            replyText = recognize_func(openai_api_base + "/chat/completions",
                                       openai_api_key, prompt, file_url,
                                       file_recognize_model, session_id)
        except Exception as e:
            replyText = error_message
            logger.error("Processing failed: {}".format(str(e)))
    else:
        replyText = error_message
    reply_message_method(True, replyText, e_context)


class Common:

    @staticmethod
    def process_image(openai_api_base, openai_api_key, image_recognize_model, image_recognize_prompt, e_context):
        process_image_content(openai_api_base, openai_api_key, image_recognize_model,
                              image_recognize_prompt, util.recognize_image,
                              "🥰请先发送图片给我,我将为您进行图像分析",
                              MessageReply.reply_Text_Message, e_context)

    @staticmethod
    def process_file(openai_api_base, openai_api_key, file_recognize_model, file_recognize_prompt, e_context):
        process_file_content(openai_api_base, openai_api_key, file_recognize_model,
                             file_recognize_prompt, util.recognize_file,
                             "🥰请先发送文件给我,我将为您进行文件分析",
                             MessageReply.reply_Text_Message, e_context)

    # 图片创作
    @staticmethod
    def process_image_create(is_use_fanyi, bot_prompt, rules, Model, request_bot_name, start_args, params, options,
                             is_wecom, e_context):
        try:
            context = e_context['context']
            content = MessageHandle.init_content(e_context)
            session_id = context.kwargs.get('session_id')

            text = "🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
            MessageReply.tem_reply_Text_Message(text, e_context)

            SDReply.create_Image(content, is_use_fanyi, bot_prompt, rules, Model, request_bot_name, start_args, params,
                                 options, session_id, is_wecom, e_context)
        except Exception as e:
            raise RuntimeError(f"图片处理发生错误: {e}") from e

    # 图片自定义图生图
    @staticmethod
    def process_image_custom(is_use_fanyi, bot_prompt, Model, request_bot_name, start_args,
                             negative_prompt, maxsize, is_wecom, e_context):
        try:
            context = e_context['context']
            content = MessageHandle.init_content(e_context)
            session_id = context.kwargs.get('session_id')

            text = "🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
            MessageReply.tem_reply_Text_Message(text, e_context)

            SDReply.custom_Image(content, is_use_fanyi, bot_prompt, Model, request_bot_name, start_args,
                                 session_id, negative_prompt, maxsize, is_wecom, e_context)
        except Exception as e:
            raise RuntimeError(f"图片处理发生错误: {e}") from e

    # 图片按照config配置图生图
    @staticmethod
    def process_image_change(Model, request_bot_name, start_args, default_options,
                             roleRule_options, denoising_strength, cfg_scale,
                             prompt, negative_prompt, title, maxsize: int, is_wecom, e_context):
        try:
            content = MessageHandle.init_content(e_context)

            text = "🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
            MessageReply.tem_reply_Text_Message(text, e_context)

            SDReply.change_Image(content, Model, request_bot_name, start_args, default_options,
                                 roleRule_options, denoising_strength, cfg_scale,
                                 prompt, negative_prompt, title, maxsize, is_wecom, e_context)
        except Exception as e:
            raise RuntimeError(f"图片处理发生错误: {e}") from e

    # 图片变换
    @staticmethod
    def process_image_transform(Model, request_bot_name, start_args, use_https, host, port, file_url,
                                prompt, negative_prompt, maxsize: int, is_wecom, e_context):
        try:
            content = MessageHandle.init_content(e_context)

            text = "🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
            MessageReply.tem_reply_Text_Message(text, e_context)

            SDReply.transform_Image(content, Model, request_bot_name, start_args, use_https, host, port, file_url,
                                    prompt, negative_prompt, maxsize, is_wecom, e_context)
        except Exception as e:
            raise RuntimeError(f"图片处理发生错误: {e}") from e

    # 图片放大
    @staticmethod
    def process_image_large(use_https, host, port, file_url, e_context):
        content = MessageHandle.init_content(e_context)

        text = "🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
        MessageReply.tem_reply_Text_Message(text, e_context)
        try:
            SDReply.large_Image(content, use_https, host, port, file_url, e_context)
        except Exception as e:
            raise RuntimeError(f"图片处理发生错误: {e}") from e

    # 接收图片初始化发送信息
    @staticmethod
    def process_init_image(request_bot_name, role_options, use_stable_diffusion,
                           use_music_handle, use_file_handle, is_wecom, e_context):
        content = MessageHandle.init_content(e_context)
        file_content = urllib.parse.quote(content)
        if e_context['context'].type == ContextType.IMAGE:
            replyText = MessageType.in_image_reply(file_content, request_bot_name, role_options, use_stable_diffusion,
                                                   use_music_handle, use_file_handle, is_wecom)
            MessageReply.reply_Text_Message(True, replyText, e_context)

    # 接收图片链接初始化发送信息
    @staticmethod
    def process_init_image_url(request_bot_name, role_options, use_stable_diffusion,
                               use_music_handle, use_file_handle, is_wecom, e_context):
        try:
            content = MessageHandle.init_content(e_context)
            response = requests.get(content)
            file_content = str(int(time.time())) + ".jpg"
            if response.status_code == 200:
                with open(file_content, 'wb') as file:
                    file.write(response.content)
                    replyText = MessageType.in_image_reply(file_content, request_bot_name, role_options,
                                                           use_stable_diffusion, use_file_handle, use_music_handle, is_wecom)
                    MessageReply.reply_Text_Message(True, replyText, e_context)
            else:
                logger.error("下载失败")
                e_context.action = EventAction.BREAK_PASS
        except Exception as e:
            raise RuntimeError(f"图片处理发生错误: {e}") from e

    # 处理百度图片(图像修复)
    @staticmethod
    def process_baidu_image(baidu_api_key, baidu_secret_key, e_context):
        try:
            content = MessageHandle.init_content(e_context)
            file_content = content.split()[2]

            if os.path.isfile(file_content):
                encoded_image = Baidu_Image.read_and_encode_image(file_content)
                if not encoded_image:
                    return
                MessageReply.tem_reply_Text_Message(
                    "🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持",
                    e_context
                )
                access_token = Baidu_Image.get_access_token(baidu_api_key, baidu_secret_key)
                if not access_token:
                    MessageReply.reply_Error_Message(True, "无法获取百度AI接口访问令牌", e_context)
                    return
                processed_image_data = Baidu_Image.process_image(encoded_image, access_token)
                if processed_image_data:
                    Baidu_Image.reply_image(processed_image_data, file_content, e_context)
                else:
                    MessageReply.reply_Error_Message(True, "未找到转换后的图像数据", e_context)
            else:
                MessageReply.reply_Error_Message(True, "🥰请先发送图片给我,我将为您进行图像修复", e_context)
        except Exception as e:
            raise RuntimeError(f"图片处理发生错误: {e}") from e

    @staticmethod
    def process_text_music(bot_prompt, url, key, model, prompt, is_wecom, e_context):
        try:
            url = url + "/chat/completions"
            music_handle.text_to_music(bot_prompt, True, url, key, prompt, model, is_wecom, e_context)
        except Exception as e:
            raise RuntimeError(f"文生音乐发生错误: {e}") from e

    @staticmethod
    def process_image_music(url, key, image_recognize_model, suno_model, bot_prompt, is_wecom, e_context):
        try:
            url = url + "/chat/completions"
            image_text = process_image_music_content(url, key, image_recognize_model, bot_prompt, util.recognize_image,
                                                     MessageReply.reply_Text_Message, e_context)
            music_handle.text_to_music(bot_prompt, False, url, key, image_text, suno_model, is_wecom, e_context)
        except Exception as e:
            raise RuntimeError(f"图生音乐发生错误: {e}") from e
