import io
import os
import time

import requests
import webuiapi
from PIL import Image

from common.log import logger
from plugins.pictureChange.message import message_reply as message_reply, message_type
from plugins.pictureChange.util import translate_prompt, image_handle, file_handle


# 用于回复图片消息
def reply_image(result, start_time, file_content, request_bot_name, modelName, image_type, is_wecom, e_context):
    # 发送图片
    b_img = io.BytesIO()
    result.image.save(b_img, format="PNG")
    message_reply.tem_reply_Image_Message(b_img, e_context)
    all_seeds = result.info['all_seeds']
    imageMessage_reply(all_seeds, start_time, request_bot_name, modelName, image_type, is_wecom, e_context)
    file_handle.delete_file(file_content)


#  用于图片信息文本回复
def imageMessage_reply(all_seeds, start_time, request_bot_name, modelName, image_type, is_wecom, e_context):
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    replyText = message_type.on_image_reply(request_bot_name, image_type, all_seeds,
                                            modelName, minutes, seconds, is_wecom)
    message_reply.reply_Text_Message(True, replyText, e_context)


# 用于stable_diffusion创建图片
def create_Image(content, is_use_fanyi, bot_prompt, rules, Model,
                 request_bot_name, start_args, params, options,
                 session_id, is_wecom, e_context):
    try:
        start_time = time.time()
        if ":" in content:
            keywords, prompt = content.split(":", 1)
        else:
            keywords = content
            prompt = ""
        keywords = keywords.split()
        unused_keywords = []

        rule_params = {}
        rule_options = {}

        # Match keywords to rules
        for keyword in keywords:
            for rule in rules:
                if keyword in rule["keywords"]:
                    logger.info("[SD] keyword matched: %s" % keyword)
                    rule_params.update(rule["params"])
                    if "options" in rule:
                        rule_options.update(rule["options"])
                    break
            else:
                unused_keywords.append(keyword)
                logger.info("[SD] keyword not matched: %s" % keyword)

        params["prompt"] = params.get("prompt", "")

        if unused_keywords:
            if prompt:
                prompt += f", {', '.join(unused_keywords)}"
            else:
                prompt = ', '.join(unused_keywords)
        translate_prompt.translatePrompt(is_use_fanyi, bot_prompt, prompt, params, session_id)
        api = webuiapi.WebUIApi(**start_args)
        if options:
            logger.info("[SD] cover options={}".format(options))
            api.set_options(options)
        logger.info("[SD] params={}".format(params))

        result = api.txt2img(
            batch_size=4,
            n_iter=1,
            do_not_save_samples=True,
            do_not_save_grid=True,
            save_images=True,
            **params
        )
        # Process model name
        model = options["sd_model_checkpoint"]
        modelName = next((member.name for member in Model if model == member.value), model)
        logger.info(f"SD使用了其他模型：{modelName}")

        # Send image and additional instructions
        b_img = io.BytesIO()
        result.image.save(b_img, format="PNG")
        message_reply.tem_reply_Image_Message(b_img, e_context)
        all_seeds = result.info['all_seeds']
        imageMessage_reply(all_seeds, start_time, request_bot_name, modelName, "txt2img-images", is_wecom, e_context)

    except Exception as e:
        logger.error(f"【SD】创作图片时出现错误：{e}")
        replyText = "hum......，请联系管理员或者稍后再试吧！"
        message_reply.reply_Error_Message(True, replyText, e_context)
        return


# 用于stable_diffusion自定义图生图
def custom_Image(content, is_use_fanyi, bot_prompt, Model, request_bot_name, start_args, session_id,
                 negative_prompt, maxsize: int, is_wecom, e_context):
    start_time = time.time()
    start_index = content.find("tmp/")
    end_index = content.find(".png")
    file_content = content[start_index:end_index + 4]
    start_index = content.find("[关键词]") + 5
    keywords = content[start_index:].split()
    keywords_string = ' '.join(keywords)
    prompt = keywords_string
    prompt = translate_prompt.simple_translatePrompt(is_use_fanyi, bot_prompt, prompt, session_id)
    logger.info(f"[SD] prompt: {prompt}")

    images = []
    logger.info(f"{file_content}")
    if os.path.isfile(file_content):
        try:
            # 从文件中读取数据
            with open(file_content, 'rb') as file:
                image_data = file.read()
                logger.info("图片读取成功")
        except Exception as e:
            logger.error(f"读取图片数据时出现错误：{e}")
            message_reply.reply_Error_Message(True, str(e), e_context)
            return

        try:
            image = Image.open(io.BytesIO(image_data))
            images.append(image)
            width, height = image.size
            width, height = image_handle.adjust_image(width, height, maxsize)
            logger.info(f"width: {width} height: {height}")

        except Exception as e:
            message_reply.reply_Error_Message(True, str(e), e_context)
            return

        default_options = {
            "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
        }
        api = webuiapi.WebUIApi(**start_args)
        api.set_options(default_options)
        # 调用img2img函数，并传递修改后的images列表作为参数
        result = api.img2img(
            images=images,
            steps=20,
            denoising_strength=0.70,
            cfg_scale=7.0,
            width=width,
            height=height,
            batch_size=4,
            n_iter=1,
            do_not_save_samples=True,
            do_not_save_grid=True,
            save_images=True,
            prompt=prompt,
            negative_prompt=negative_prompt,
        )
        model = default_options["sd_model_checkpoint"]
        for member in Model:
            if model == member.value:
                modelName = member.name
                break
        else:
            modelName = model
            logger.info("使用了其他模型")
        # 发送图片
        reply_image(result, start_time, file_content, request_bot_name, modelName, "img2img-images", is_wecom,
                    e_context)

    else:
        replyText = f"🥰请先发送图片给我,我将为您进行图片操作"
        message_reply.reply_Text_Message(True, replyText, e_context)


# 用于stable_diffusion按照config.json变换图生图
def change_Image(content, Model, request_bot_name, start_args, default_options,
                 roleRule_options, denoising_strength, cfg_scale,
                 prompt, negative_prompt, title, maxsize: int, is_wecom, e_context):
    start_time = time.time()
    file_content = content.split()[2]
    images = []
    logger.info(f"{file_content}")
    if os.path.isfile(file_content):
        try:
            # 从文件中读取数据
            with open(file_content, 'rb') as file:
                image_data = file.read()
                logger.info("图片读取成功")
        except Exception as e:
            logger.error(f"读取图片数据时出现错误：{e}")
            message_reply.reply_Error_Message(True, str(e), e_context)
            return

        image = Image.open(io.BytesIO(image_data))
        width, height = image.size
        width, height = image_handle.adjust_image(width, height, int(maxsize))
        logger.info(f"width: {width} height: {height}")
        images.append(image)

        options = {**default_options, **roleRule_options}
        # 更改固定模型
        api = webuiapi.WebUIApi(**start_args)
        api.set_options(options)
        # 调用img2img函数，并传递修改后的images列表作为参数
        result = api.img2img(
            images=images,
            steps=20,
            denoising_strength=denoising_strength,
            cfg_scale=cfg_scale,
            width=width,
            height=height,
            batch_size=4,
            n_iter=1,
            do_not_save_samples=True,
            do_not_save_grid=True,
            save_images=True,
            prompt=prompt,
            negative_prompt=negative_prompt,
        )

        model = options["sd_model_checkpoint"]
        for member in Model:
            if model == member.value:
                modelName = member.name
                break
        else:
            modelName = model
            logger.info("使用了其他模型")

        # 发送图片
        reply_image(result, start_time, file_content, request_bot_name, modelName, "img2img-images", is_wecom,
                    e_context)

    else:
        replyText = f"🥰请先发送图片给我,我将为您进行{title}"
        message_reply.reply_Text_Message(True, replyText, e_context)


# 用于stable_diffusion变换图生图
def transform_Image(content, Model, request_bot_name, start_args, use_https, host, port, file_url,
                    prompt, negative_prompt, maxsize: int, is_wecom, e_context):
    start_time = time.time()
    file_content = content.split()[2]
    images = []
    logger.info(f"{file_content}")
    model = getattr(Model, content.split()[3]).value
    image_url = image_handle.format_image_url(use_https, host, port, file_url, file_content)
    # 发送 GET 请求获取图像数据
    response = requests.get(image_url)
    # 检查响应状态码是否为 200，表示请求成功
    if response.status_code == 200:
        # 获取图像的二进制数据
        image_data = response.content
        # 将二进制图像数据转换为 PIL Image 对象
        image = Image.open(io.BytesIO(image_data))
        width, height = image.size
        width, height = image_handle.adjust_image(width, height, int(maxsize))
        # 将PIL Image对象添加到images列表中
        images.append(image)
        default_options = {
            "sd_model_checkpoint": model
        }
        api = webuiapi.WebUIApi(**start_args)
        api.set_options(default_options)
        # 调用img2img函数，并传递修改后的images列表作为参数
        result = api.img2img(
            images=images,
            steps=20,
            denoising_strength=0.5,
            cfg_scale=7.0,
            batch_size=4,
            n_iter=1,
            do_not_save_samples=True,
            do_not_save_grid=True,
            save_images=True,
            width=width,
            height=height,
            prompt=prompt,
            negative_prompt=negative_prompt,
        )
        # 发送图片
        for member in Model:
            if model == member.value:
                modelName = member.name
                break
        else:
            modelName = model
            logger.info("使用了其他模型")

        # 发送图片
        reply_image(result, start_time, file_content, request_bot_name, modelName, "img2img-images", is_wecom,
                    e_context)

    else:
        replyText = f"🥰请先发送图片给我,我将为您进行图片操作"
        message_reply.reply_Text_Message(True, replyText, e_context)


# 用于放大图片
def large_Image(content, use_https, host, port, file_url, e_context):
    try:
        file_content = content.split()[2]
        logger.info(f"{file_content}")
        image_url = image_handle.format_image_url(use_https, host, port, file_url, file_content)
        logger.info(f"图片地址为：{image_url}")
        response = requests.get(image_url)
        response.raise_for_status()
        message_reply.reply_Image_Url_Message(True, image_url, e_context)
    except Exception as e:
        replyText = "[😭转换图片失败]" + str(e) + "\n快联系管理员解决问题吧🥰🥰🥰"
        message_reply.reply_Text_Message(True, replyText, e_context)
