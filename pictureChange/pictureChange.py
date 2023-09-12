import io
import json
import os
import base64
import urllib
import time
import requests
import webuiapi
import langid
import plugins
from bridge.bridge import Bridge
from oauthlib.common import urlencoded
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from config import conf
from plugins import *
from PIL import Image
import urllib.parse

@plugins.register(name="pictureChange", desc="利用百度云AI和stable-diffusion webui来画图,图生图", version="1.6.1", author="yangyang")
class pictureChange(Plugin):
    def __init__(self):
        super().__init__()
        curdir = os.path.dirname(__file__)
        config_path = os.path.join(curdir, "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.API_KEY = config["api_key"]
                self.SECRET_KEY = config["secret_key"]
                self.rules = config["rules"]
                defaults = config["defaults"]
                self.default_params = defaults["params"]
                self.default_options = defaults["options"]
                self.role_options = config["roles"]
                self.start_args = config["start"]
                self.other_user_id = config["use_group"]
                self.max_number = config["max_number"]
                self.use_number = 0
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[SD] inited")
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                logger.warn(f"[SD] init failed, {config_path} not found.")
            else:
                logger.warn("[SD] init failed.")
            raise e
    
    def on_handle_context(self, e_context: EventContext):
        temimages = []
        api = webuiapi.WebUIApi(**self.start_args)
        # if e_context['context'].type != ContextType.IMAGE_CREATE:
        #     return
        reply = Reply()
        channel = e_context['channel']
        if ReplyType.IMAGE in channel.NOT_SUPPORT_REPLYTYPE:
            return
        context = e_context['context']
        msg: ChatMessage = context["msg"]
        content = context.content
        file_content = content
        check_exist = False
        denoising_strength = 0
        cfg_scale = 0
        prompt = ""
        negative_prompt = ""  
        title = "" 
        roleRule_options = {}
        isgroup = context["msg"].is_group
        channel = e_context["channel"]    
        for role in self.role_options:
            if content.startswith(role['title']+" "):
                title = role['title']
                denoising_strength = role['denoising_strength']
                cfg_scale = role['cfg_scale']
                prompt = role['prompt']
                negative_prompt = role['negative_prompt']
                if "options" in role:
                    for key in role["options"]:
                        roleRule_options[key] = role["options"][key]
                check_exist = True
                break
        if isgroup:
            if content == "开启图生图":
                if context["msg"].other_user_id in self.other_user_id:
                    reply.type = ReplyType.TEXT
                    replyText = f"🤖图生图模式已开启，请勿重复开启"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                else:
                    self.other_user_id.append(context["msg"].other_user_id)
                    curdir = os.path.dirname(__file__)
                    config_path = os.path.join(curdir, "config.json")
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        config["use_group"].append(context["msg"].other_user_id)
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)
                    reply.type = ReplyType.TEXT
                    replyText = f"🥰图生图模式已开启，请发送图片给我,我将为您进行图像处理"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                return
                
            elif content == "关闭图生图":
                if context["msg"].other_user_id in self.other_user_id:
                    try:
                        self.other_user_id.remove(context["msg"].other_user_id)
                        curdir = os.path.dirname(__file__)
                        config_path = os.path.join(curdir, "config.json")
                        with open(config_path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                            config["use_group"].remove(context["msg"].other_user_id)
                        with open(config_path, "w", encoding="utf-8") as f:
                            json.dump(config, f, indent=4, ensure_ascii=False)
                        reply.type = ReplyType.TEXT
                        replyText = "🥰图生图模式已关闭"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    except Exception as e:
                        # 处理异常情况的代码
                        reply.type = ReplyType.TEXT
                        replyText = "😭关闭失败：" + str(e)
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                else:
                        # 处理异常情况的代码
                        reply.type = ReplyType.TEXT
                        replyText = "😭请检查图生图是否开启"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                return
        
            elif e_context['context'].type == ContextType.IMAGE_CREATE:
                if self.use_number >= self.max_number:
                        reply.type = ReplyType.TEXT
                        replyText = f"🧸当前排队人数为{str(self.use_number - self.max_number + 1)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                else:
                    self.use_number += 1
                    content = e_context['context'].content[:]
                    # 解析用户输入 如"横版 高清 二次元:cat"
                    if ":" in content:
                        keywords, prompt = content.split(":", 1)
                    else:
                        keywords = content
                        prompt = ""
                    keywords = keywords.split()
                    unused_keywords = []
                    text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                    temreply = Reply(ReplyType.TEXT, text)
                    channel._send(temreply, e_context["context"])
                    if "help" in keywords or "帮助" in keywords:
                        reply.type = ReplyType.INFO
                        reply.content = self.get_help_text()
                    else:
                        rule_params = {}
                        rule_options = {}
                        for keyword in keywords:
                            matched = False
                            for rule in self.rules:
                                if keyword in rule["keywords"]:
                                    for key in rule["params"]:
                                        rule_params[key] = rule["params"][key]
                                    if "options" in rule:
                                        for key in rule["options"]:
                                            rule_options[key] = rule["options"][key]
                                    matched = True
                                    break  # 一个关键词只匹配一个规则
                            if not matched:
                                unused_keywords.append(keyword)
                                logger.info("[SD] keyword not matched: %s" % keyword)
                        
                        params = {**self.default_params, **rule_params}
                        options = {**self.default_options, **rule_options}
                        params["prompt"] = params.get("prompt", "")
                        if unused_keywords:
                            if prompt:
                                prompt += f", {', '.join(unused_keywords)}"
                            else:
                                prompt = ', '.join(unused_keywords)
                        if prompt:
                            lang = langid.classify(prompt)[0]
                            if lang != "en":
                                logger.info("[SD] translate prompt from {} to en".format(lang))
                                try:
                                    prompt = Bridge().fetch_translate(prompt, to_lang= "en")
                                except Exception as e:
                                    logger.info("[SD] translate failed: {}".format(e))
                                logger.info("[SD] translated prompt={}".format(prompt))
                            params["prompt"] += f", {prompt}"
                        if len(options) > 0:
                            logger.info("[SD] cover options={}".format(options))
                            api.set_options(options)
                        logger.info("[SD] params={}".format(params))
                        result = api.txt2img(
                            **params
                        )
                        reply.type = ReplyType.IMAGE
                        b_img = io.BytesIO()
                        result.image.save(b_img, format="PNG")
                        reply.content = b_img
                        e_context['reply'] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        self.use_number -= 1
                        return

            elif context["msg"].other_user_id in self.other_user_id:
                try:
                    if e_context['context'].type == ContextType.IMAGE:
                        if self.use_number >= self.max_number:
                            reply.type = ReplyType.TEXT
                            replyText = f"🧸当前排队人数为{str(self.use_number - self.max_number + 1)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
                            reply.content = replyText
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            return
                        else:
                            self.use_number += 1
                            msg.prepare()
                            reply.type = ReplyType.TEXT
    
                            replyText = f"🥰 您的图片编号:\n💖 {file_content}\n\n❗ 请输入指令,以进行图片操作\n✅ 支持指令\n\n@羊羊 🌈 图像动漫化 {file_content}\n\n@羊羊🤖 图像修复 {file_content}"
                            for role in self.role_options:
                                replyText += f"\n\n@羊羊 {role['title']} {file_content}"
                            replyText += f"\n\n@羊羊 🎡 自定义 {file_content} [关键词] 例如 黑色头发 白色短袖 等关键词"
                            replyText += f"\n\n@羊羊 ❎ 暂不处理 {file_content}"
                            replyText += "\n\n🚀 发送指令后，请耐心等待一至两分钟，作品将很快呈现出来！"
                            reply.content = replyText
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            return
                    
                    elif any(ext in content for ext in ["jpg", "jpeg", "png", "gif", "webp"]) and (content.startswith("http://") or content.startswith("https://")):
                        if self.use_number >= self.max_number:
                            reply.type = ReplyType.TEXT
                            replyText = f"🧸当前排队人数为{str(self.use_number - self.max_number + 1)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
                            reply.content = replyText
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            return
                        else:
                            self.use_number += 1
                            response = requests.get(content)
                            file_content = str(int(time.time())) + ".jpg"
                            if response.status_code == 200:
                                with open(file_content, 'wb') as file:
                                    file.write(response.content)
                            else:
                                print("下载失败")
                            reply.type = ReplyType.TEXT
                            replyText = f"🥰 您的图片编号:\n💖 {file_content}\n\n❗ 请输入指令,以进行图片操作\n✅ 支持指令\n\n@羊羊 🌈 图像动漫化 {file_content}\n\n@羊羊🤖 图像修复 {file_content}"
                            for role in self.role_options:
                                replyText += f"\n\n@羊羊 {role['title']} {file_content}"
                            replyText += f"\n\n@羊羊 🎡 自定义 {file_content} [关键词] 例如 黑色头发 白色短袖 等关键词"
                            replyText += f"\n\n@羊羊 ❎ 暂不处理 {file_content}"
                            replyText += "\n\n🚀 发送指令后，请耐心等待一至两分钟，作品将很快呈现出来！"
                            reply.content = replyText
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            return
                        
                    elif content.startswith("❎ 暂不处理 "):
                        file_content = content[len("❎ 暂不处理 "):]
                        # 删除文件
                        reply.type = ReplyType.TEXT
                        replyText = ""
                        if os.path.isfile(file_content):
                            os.remove(file_content)
                            replyText = "🥰文件已成功删除"
                        else:
                            replyText = "😭文件不存在或已删除"
                        reply.content = replyText
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        self.use_number -= 1
                        return
                    
                    elif content.startswith("🌈 图像动漫化 "):
                        file_content = content[len("🌈 图像动漫化 "):]
                        if os.path.isfile(file_content):
                            try:
                                with open(file_content, 'rb') as file:
                                    image_data = file.read()
                                    logger.info("图片获取成功")
                                    encoded_image = base64.b64encode(image_data).decode('utf-8')
                                    text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                                    temreply = Reply(ReplyType.TEXT, text)
                                    channel._send(temreply, e_context["context"])
                                    if urlencoded:
                                        encoded_image = urllib.parse.quote_plus(encoded_image)
                                    payload = "image=" + encoded_image
                            except Exception as e:
                                logger.error(f"处理文件数据时出现错误：{e}")
                                return
                            # 获取百度AI接口访问令牌
                            token_url = "https://aip.baidubce.com/oauth/2.0/token"
                            token_params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
                            access_token = requests.post(token_url, params=token_params).json().get("access_token")
                            
                            if not access_token:
                                logger.error("无法获取百度AI接口访问令牌")
                                return
                            
                            process_url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/selfie_anime?access_token={access_token}"
                            headers = {
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Accept': 'application/json'
                            }
                
                            response = requests.post(process_url, headers=headers, data=payload)
                
                            if response.status_code == 200:
                                base64_image_data = response.json().get('image')
                                if base64_image_data:
                                    # 解码Base64编码的图像数据
                                    image_data = base64.b64decode(base64_image_data)
                                    # 将图像数据写入图片文件
                                    image_storage = io.BytesIO()
                                    image_storage.write(image_data)
                                    image_storage.seek(0)
                                    
                                    reply.type = ReplyType.IMAGE
                                    reply.content = image_storage
                                    e_context["reply"] = reply
                
                                    # 图像处理成功后删除文件
                                    if os.path.isfile(file_content):
                                        os.remove(file_content)
                                        logger.info("文件已成功删除")
                                    else:
                                        logger.error("文件不存在")
                                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                                    self.use_number -= 1
                                    return
                                else:
                                    logger.error("未找到转换后的图像数据")
                            else:
                                logger.error("API请求失败")
                        else:
                            
                            reply.type = ReplyType.TEXT
                            replyText = f"🥰请先发送图片给我,我将为您进行🌈 图像动漫化"
                            reply.content = replyText
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            return
                            
                            
                    elif content.startswith("🤖 图像修复 ") :
                        file_content = content[len("🤖 图像修复 "):]
                        if os.path.isfile(file_content):
                            try:
                                with open(file_content, 'rb') as file:
                                    image_data = file.read()
                                    logger.info("图片获取成功")
                                    encoded_image = base64.b64encode(image_data).decode('utf-8')
                                    text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                                    temreply = Reply(ReplyType.TEXT, text)
                                    channel._send(temreply, e_context["context"])
                                    if urlencoded:
                                        encoded_image = urllib.parse.quote_plus(encoded_image)
                                    payload = "image=" + encoded_image
                            except Exception as e:
                                logger.error(f"处理文件数据时出现错误：{e}")
                                return
                            # 获取百度AI接口访问令牌
                            token_url = "https://aip.baidubce.com/oauth/2.0/token"
                            token_params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
                            access_token = requests.post(token_url, params=token_params).json().get("access_token")
                            
                            if not access_token:
                                logger.error("无法获取百度AI接口访问令牌")
                                return
                            
                            process_url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/image_definition_enhance?access_token={access_token}"
                            headers = {
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Accept': 'application/json'
                            }
                
                            response = requests.post(process_url, headers=headers, data=payload)
                
                            if response.status_code == 200:
                                base64_image_data = response.json().get('image')
                                if base64_image_data:
                                    # 解码Base64编码的图像数据
                                    image_data = base64.b64decode(base64_image_data)
                                    # 将图像数据写入图片文件
                                    image_storage = io.BytesIO()
                                    image_storage.write(image_data)
                                    image_storage.seek(0)
                                    
                                    reply.type = ReplyType.IMAGE
                                    reply.content = image_storage
                                    e_context["reply"] = reply
                
                                    # 图像处理成功后删除文件
                                    if os.path.isfile(file_content):
                                        os.remove(file_content)
                                        logger.info("文件已成功删除")
                                    else:
                                        logger.error("文件不存在")
                                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                                    self.use_number -= 1
                                    return
                                else:
                                    logger.error("未找到转换后的图像数据")
                            else:
                                logger.error("API请求失败")
                        else:
                            
                            reply.type = ReplyType.TEXT
                            replyText = f"🥰请先发送图片给我,我将为您进行图像修复"
                            reply.content = replyText
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            return
                    
                    elif content.startswith("🎡 自定义 "):
                        # Extracting the filename
                        start_index = content.find("tmp/")
                        end_index = content.find(".png")
                        file_content = content[start_index:end_index + 4]  # Adding 4 to include the extension
                        start_index = content.find("[关键词]") + 5  # Adding 3 to skip the space
                        keywords = content[start_index:].split()
                        keywords_string = ' '.join(keywords)
                        prompt += keywords_string
                        lang = langid.classify(prompt)[0]
                        if lang != "en":
                            # 非英文，进行翻译
                            logger.info("[SD] Translating prompt from {} to en".format(lang))
                            try:
                                prompt = Bridge().fetch_translate(prompt, to_lang="en")
                            except Exception as e:
                                logger.error("Translation failed: {}".format(str(e)))
                        else:
                            # 英文，无需翻译
                            logger.info("[SD] Prompt is already in English")
                        if os.path.isfile(file_content):
                            try:
                                # 从文件中读取数据
                                with open(file_content, 'rb') as file:
                                    image_data = file.read()
                                    logger.info("图片读取成功")
                            except Exception as e:
                                logger.error(f"读取图片数据时出现错误：{e}")
                                return
                            # print("匹配的标题:", title)
                            # print("Prompt:", prompt)
                            # print("Negative Prompt:", negative_prompt)
                            # print("Denoising Strength:", denoising_strength)
                            # print("Cfg Scale:", cfg_scale)
                            # 调用img2img函数，并传递修改后的images列表作为参数
                            # 将二进制图像数据转换为PIL Image对象
                            text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                            temreply = Reply(ReplyType.TEXT, text)
                            channel._send(temreply, e_context["context"])
                            image = Image.open(io.BytesIO(image_data))
                            width, height = image.size
                            temwidth = 0.38 * width
                            temheight = 0.38 * height
                            # 将PIL Image对象添加到images列表中
                            temimages.append(image)
                            default_options = {
                                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
                            }
                            # 更改固定模型
                            api.set_options(default_options)
                            # 调用img2img函数，并传递修改后的images列表作为参数
                            result = api.img2img(
                                images = temimages,
                                steps = 15,
                                denoising_strength = 0.35,
                                cfg_scale = 7.0,
                                width = temwidth,
                                height = temheight,
                                prompt = prompt,
                                negative_prompt = "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure,",
                                
                            )
                            reply.type = ReplyType.IMAGE
                            b_img = io.BytesIO()
                            result.image.save(b_img, format="PNG")
                            reply.content = b_img
                            e_context['reply'] = reply
                            if os.path.isfile(file_content):
                                os.remove(file_content)
                                logger.info("文件已成功删除")
                            else:
                                logger.error("文件不存在")
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            self.use_number -= 1
                            return
                        else:
                            reply.type = ReplyType.TEXT
                            replyText = f"🥰请先发送图片给我,我将为您进行自定义图像处理"
                            reply.content = replyText
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            return
                    
                    elif check_exist:
                        file_content = content[len(title+" "):]
                        if os.path.isfile(file_content):
                            try:
                                # 从文件中读取数据
                                with open(file_content, 'rb') as file:
                                    image_data = file.read()
                                    logger.info("图片读取成功")
                            except Exception as e:
                                logger.error(f"读取图片数据时出现错误：{e}")
                                return
                            # print("匹配的标题:", title)
                            # print("Prompt:", prompt)
                            # print("Negative Prompt:", negative_prompt)
                            # print("Denoising Strength:", denoising_strength)
                            # print("Cfg Scale:", cfg_scale)
                            # 调用img2img函数，并传递修改后的images列表作为参数
                            # 将二进制图像数据转换为PIL Image对象
                            text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                            temreply = Reply(ReplyType.TEXT, text)
                            channel._send(temreply, e_context["context"])
                            image = Image.open(io.BytesIO(image_data))
                            width, height = image.size
                            temwidth = 0.38 * width
                            temheight = 0.38 * height
                            # 将PIL Image对象添加到images列表中
                            temimages.append(image)
                            options = {**self.default_options, **roleRule_options}
                            # 更改固定模型
                            api.set_options(options)
                            # 调用img2img函数，并传递修改后的images列表作为参数
                            result = api.img2img(
                                images = temimages,
                                steps = 15,
                                denoising_strength = denoising_strength,
                                cfg_scale = cfg_scale,
                                width = temwidth,
                                height = temheight,
                                prompt = prompt,
                                negative_prompt = negative_prompt,
                                
                            )
                            reply.type = ReplyType.IMAGE
                            b_img = io.BytesIO()
                            result.image.save(b_img, format="PNG")
                            reply.content = b_img
                            if os.path.isfile(file_content):
                                os.remove(file_content)
                                logger.info("文件已成功删除")
                            else:
                                logger.error("文件不存在")
                            e_context['reply'] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            self.use_number -= 1
                            return
                        else:
                            reply.type = ReplyType.TEXT
                            replyText = f"🥰请先发送图片给我,我将为您进行{role['title']}"
                            reply.content = replyText
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            return
                        
                except Exception as e:
                    reply.content = "[pictureChange画图失败] "+str(e)
                    reply = Reply(ReplyType.ERROR, reply.content)
                    logger.error("[pictureChange画图失败] exception: %s" % e)
                    channel._send(reply, e_context["context"])
                    if os.path.isfile(file_content):
                        os.remove(file_content)
                        logger.info("文件已成功删除")
                    if e_context['context'].type == ContextType.IMAGE_CREATE:
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        self.use_number -= 1
                    else:
                        e_context.action = EventAction.CONTINUE  # 事件继续，交付给下个插件或默认逻辑
                        self.use_number -= 1
                        return
            else:
                e_context.action = EventAction.CONTINUE  # 事件继续，交付给下个插件或默认逻辑'
                return
                
        else:
            try:
                if e_context['context'].type == ContextType.IMAGE:
                    if self.use_number >= self.max_number:
                        reply.type = ReplyType.TEXT
                        replyText = f"🧸当前排队人数为{str(self.use_number - self.max_number + 1)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                    else:
                        self.use_number += 1
                        msg.prepare()
                        reply.type = ReplyType.TEXT
                        replyText = f"🥰 您的图片编号:\n💖 {file_content}\n\n❗ 请输入指令,以进行图片操作\n✅ 支持指令\n\n@羊羊 🌈 图像动漫化 {file_content}\n\n@羊羊🤖 图像修复 {file_content}"
                        for role in self.role_options:
                            replyText += f"\n\n@羊羊 {role['title']} {file_content}"
                        replyText += f"\n\n@羊羊 🎡 自定义 {file_content} [关键词] 例如 黑色头发 白色短袖 等关键词"
                        replyText += f"\n\n@羊羊 ❎ 暂不处理 {file_content}"
                        replyText += "\n\n🚀 发送指令后，请耐心等待一至两分钟，作品将很快呈现出来！"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                
                elif any(ext in content for ext in ["jpg", "jpeg", "png", "gif", "webp"]) and (content.startswith("http://") or content.startswith("https://")):
                    if self.use_number >= self.max_number:
                        reply.type = ReplyType.TEXT
                        replyText = f"🧸当前排队人数为{str(self.use_number - self.max_number + 1)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                    else:
                        self.use_number += 1
                        response = requests.get(content)
                        file_content = str(int(time.time())) + ".jpg"
                        if response.status_code == 200:
                            with open(file_content, 'wb') as file:
                                file.write(response.content)
                        else:
                            print("下载失败")
                        reply.type = ReplyType.TEXT
                        replyText = f"🥰 您的图片编号:\n💖 {file_content}\n\n❗ 请输入指令,以进行图片操作\n✅ 支持指令\n\n@羊羊 🌈 图像动漫化 {file_content}\n\n@羊羊🤖 图像修复 {file_content}"
                        for role in self.role_options:
                            replyText += f"\n\n@羊羊 {role['title']} {file_content}"
                        replyText += f"\n\n@羊羊 🎡 自定义 {file_content} [关键词] 例如 黑色头发 白色短袖 等关键词"
                        replyText += f"\n\n@羊羊 ❎ 暂不处理 {file_content}"
                        replyText += "\n\n🚀 发送指令后，请耐心等待一至两分钟，作品将很快呈现出来！"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                
                elif e_context['context'].type == ContextType.IMAGE_CREATE:
                    if self.use_number >= self.max_number:
                        reply.type = ReplyType.TEXT
                        replyText = f"🧸当前排队人数为{str(self.use_number - self.max_number + 1)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                    else:
                        self.use_number += 1
                        content = e_context['context'].content[:]
                        # 解析用户输入 如"横版 高清 二次元:cat"
                        if ":" in content:
                            keywords, prompt = content.split(":", 1)
                        else:
                            keywords = content
                            prompt = ""
            
                        keywords = keywords.split()
                        unused_keywords = []
                        text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                        temreply = Reply(ReplyType.TEXT, text)
                        channel._send(temreply, e_context["context"])
                        if "help" in keywords or "帮助" in keywords:
                            reply.type = ReplyType.INFO
                            reply.content = self.get_help_text(verbose = True)
                        else:
                            rule_params = {}
                            rule_options = {}
                            for keyword in keywords:
                                matched = False
                                for rule in self.rules:
                                    if keyword in rule["keywords"]:
                                        for key in rule["params"]:
                                            rule_params[key] = rule["params"][key]
                                        if "options" in rule:
                                            for key in rule["options"]:
                                                rule_options[key] = rule["options"][key]
                                        matched = True
                                        break  # 一个关键词只匹配一个规则
                                if not matched:
                                    unused_keywords.append(keyword)
                                    logger.info("[SD] keyword not matched: %s" % keyword)
                            
                            params = {**self.default_params, **rule_params}
                            options = {**self.default_options, **rule_options}
                            params["prompt"] = params.get("prompt", "")
                            if unused_keywords:
                                if prompt:
                                    prompt += f", {', '.join(unused_keywords)}"
                                else:
                                    prompt = ', '.join(unused_keywords)
                            if prompt:
                                lang = langid.classify(prompt)[0]
                                if lang != "en":
                                    logger.info("[SD] translate prompt from {} to en".format(lang))
                                    try:
                                        prompt = Bridge().fetch_translate(prompt, to_lang= "en")
                                    except Exception as e:
                                        logger.info("[SD] translate failed: {}".format(e))
                                    logger.info("[SD] translated prompt={}".format(prompt))
                                params["prompt"] += f", {prompt}"
                            if len(options) > 0:
                                logger.info("[SD] cover options={}".format(options))
                                api.set_options(options)
                            logger.info("[SD] params={}".format(params))
                            result = api.txt2img(
                                **params
                            )
                            reply.type = ReplyType.IMAGE
                            b_img = io.BytesIO()
                            result.image.save(b_img, format="PNG")
                            reply.content = b_img
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            self.use_number -= 1
                            return
                
                
                elif content.startswith("🌈 图像动漫化 "):
                    file_content = content[len("🌈 图像动漫化 "):]
                    if os.path.isfile(file_content):
                        try:
                            with open(file_content, 'rb') as file:
                                image_data = file.read()
                                logger.info("图片获取成功")
                                encoded_image = base64.b64encode(image_data).decode('utf-8')
                                text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                                temreply = Reply(ReplyType.TEXT, text)
                                channel._send(temreply, e_context["context"])
                                if urlencoded:
                                    encoded_image = urllib.parse.quote_plus(encoded_image)
                                payload = "image=" + encoded_image
                        except Exception as e:
                            logger.error(f"处理文件数据时出现错误：{e}")
                            return
                        # 获取百度AI接口访问令牌
                        token_url = "https://aip.baidubce.com/oauth/2.0/token"
                        token_params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
                        access_token = requests.post(token_url, params=token_params).json().get("access_token")
                        
                        if not access_token:
                            logger.error("无法获取百度AI接口访问令牌")
                            return
                        
                        process_url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/selfie_anime?access_token={access_token}"
                        headers = {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Accept': 'application/json'
                        }
            
                        response = requests.post(process_url, headers=headers, data=payload)
                        if response.status_code == 200:
                            base64_image_data = response.json().get('image')
                            if base64_image_data:
                                # 解码Base64编码的图像数据
                                image_data = base64.b64decode(base64_image_data)
                                # 将图像数据写入图片文件
                                image_storage = io.BytesIO()
                                image_storage.write(image_data)
                                image_storage.seek(0)
                                
                                reply.type = ReplyType.IMAGE
                                reply.content = image_storage
                                e_context["reply"] = reply
            
                                # 图像处理成功后删除文件
                                if os.path.isfile(file_content):
                                    os.remove(file_content)
                                    logger.info("文件已成功删除")
                                else:
                                    logger.error("文件不存在")
                                e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                                self.use_number -= 1
                                return
                            else:
                                logger.error("未找到转换后的图像数据")
                        else:
                            logger.error("API请求失败")
                    else:
                        
                        reply.type = ReplyType.TEXT
                        replyText = f"🥰请先发送图片给我,我将为您进行🌈 图像动漫化"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                        
                        
                elif content.startswith("🤖 图像修复 ") :
                    file_content = content[len("🤖 图像修复 "):]
                    if os.path.isfile(file_content):
                        try:
                            with open(file_content, 'rb') as file:
                                image_data = file.read()
                                logger.info("图片获取成功")
                                encoded_image = base64.b64encode(image_data).decode('utf-8')
                                text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                                temreply = Reply(ReplyType.TEXT, text)
                                channel._send(temreply, e_context["context"])
                                if urlencoded:
                                    encoded_image = urllib.parse.quote_plus(encoded_image)
                                payload = "image=" + encoded_image
                        except Exception as e:
                            logger.error(f"处理文件数据时出现错误：{e}")
                            return
                        # 获取百度AI接口访问令牌
                        token_url = "https://aip.baidubce.com/oauth/2.0/token"
                        token_params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
                        access_token = requests.post(token_url, params=token_params).json().get("access_token")
                        if not access_token:
                            logger.error("无法获取百度AI接口访问令牌")
                            return
                        
                        process_url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/image_definition_enhance?access_token={access_token}"
                        headers = {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Accept': 'application/json'
                        }
            
                        response = requests.post(process_url, headers=headers, data=payload)
            
                        if response.status_code == 200:
                            base64_image_data = response.json().get('image')
                            if base64_image_data:
                                # 解码Base64编码的图像数据
                                image_data = base64.b64decode(base64_image_data)
                                # 将图像数据写入图片文件
                                image_storage = io.BytesIO()
                                image_storage.write(image_data)
                                image_storage.seek(0)
                                
                                reply.type = ReplyType.IMAGE
                                reply.content = image_storage
                                e_context["reply"] = reply
            
                                # 图像处理成功后删除文件
                                if os.path.isfile(file_content):
                                    os.remove(file_content)
                                    logger.info("文件已成功删除")
                                else:
                                    logger.error("文件不存在")
                                e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                                self.use_number -= 1    
                                return
                            else:
                                logger.error("未找到转换后的图像数据")
                        else:
                            logger.error("API请求失败")
                    else:
                        
                        reply.type = ReplyType.TEXT
                        replyText = f"🥰请先发送图片给我,我将为您进行图像修复"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                    
                elif content.startswith("❎ 暂不处理 "):
                    file_content = content[len("❎ 暂不处理 "):]
                    # 删除文件
                    reply.type = ReplyType.TEXT
                    replyText = ""
                    if os.path.isfile(file_content):
                        os.remove(file_content)
                        replyText = "🥰文件已成功删除"
                    else:
                        replyText = "😭文件不存在或已删除"
                    reply.content = replyText
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    self.use_number -= 1
                    return
                
                elif content.startswith("🎡 自定义 "):
                    # Extracting the filename
                    start_index = content.find("tmp/")
                    end_index = content.find(".png")
                    file_content = content[start_index:end_index + 4]  # Adding 4 to include the extension
                    start_index = content.find("[关键词]") + 5  # Adding 3 to skip the space
                    keywords = content[start_index:].split()
                    keywords_string = ' '.join(keywords)
                    prompt += keywords_string
                    lang = langid.classify(prompt)[0]
                    if lang != "en":
                        # 非英文，进行翻译
                        logger.info("[SD] Translating prompt from {} to en".format(lang))
                        try:
                            prompt = Bridge().fetch_translate(prompt, to_lang="en")
                        except Exception as e:
                            logger.error("Translation failed: {}".format(str(e)))
                    else:
                        # 英文，无需翻译
                        logger.info("[SD] Prompt is already in English")
                    if os.path.isfile(file_content):
                        try:
                            # 从文件中读取数据
                            with open(file_content, 'rb') as file:
                                image_data = file.read()
                                logger.info("图片读取成功")
                        except Exception as e:
                            logger.error(f"读取图片数据时出现错误：{e}")
                            return
                        text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                        temreply = Reply(ReplyType.TEXT, text)
                        channel._send(temreply, e_context["context"])
                        # print("匹配的标题:", title)
                        # print("Prompt:", prompt)
                        # print("Negative Prompt:", negative_prompt)
                        # print("Denoising Strength:", denoising_strength)
                        # print("Cfg Scale:", cfg_scale)
                        # 调用img2img函数，并传递修改后的images列表作为参数
                        # 将二进制图像数据转换为PIL Image对象
                        image = Image.open(io.BytesIO(image_data))
                        width, height = image.size
                        temwidth = 0.38 * width
                        temheight = 0.38 * height
                        # 将PIL Image对象添加到images列表中
                        temimages.append(image)
                        default_options = {
                            "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
                        }
                        api.set_options(default_options)
                        # 调用img2img函数，并传递修改后的images列表作为参数
                        result = api.img2img(
                            images = temimages,
                            steps = 15,
                            denoising_strength = 0.35,
                            cfg_scale = 7.0,
                            width = temwidth,
                            height = temheight,
                            prompt = prompt,
                            negative_prompt = "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure,",
                            
                        )
                        reply.type = ReplyType.IMAGE
                        b_img = io.BytesIO()
                        result.image.save(b_img, format="PNG")
                        reply.content = b_img
                        e_context["reply"] = reply
                        if os.path.isfile(file_content):
                            os.remove(file_content)
                            logger.info("文件已成功删除")
                        else:
                            logger.error("文件不存在")
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        self.use_number -= 1
                        return
                    else:
                        reply.type = ReplyType.TEXT
                        replyText = f"🥰请先发送图片给我,我将为您进行自定义图像处理"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                
                elif check_exist:
                    file_content = content[len(title+" "):]
                    if os.path.isfile(file_content):
                        try:
                            # 从文件中读取数据
                            with open(file_content, 'rb') as file:
                                image_data = file.read()
                                logger.info("图片读取成功")
                        except Exception as e:
                            logger.error(f"读取图片数据时出现错误：{e}")
                            return
                        # print("匹配的标题:", title)
                        # print("Prompt:", prompt)
                        # print("Negative Prompt:", negative_prompt)
                        # print("Denoising Strength:", denoising_strength)
                        # print("Cfg Scale:", cfg_scale)
                        # 调用img2img函数，并传递修改后的images列表作为参数
                        # 将二进制图像数据转换为PIL Image对象
                        text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                        temreply = Reply(ReplyType.TEXT, text)
                        channel._send(temreply, e_context["context"])
                        image = Image.open(io.BytesIO(image_data))
                        width, height = image.size
                        temwidth = 0.38 * width
                        temheight = 0.38 * height
                        # 将PIL Image对象添加到images列表中
                        temimages.append(image)
                        options = {**self.default_options,**roleRule_options}
                        # 更改固定模型
                        api.set_options(options)
                        # 调用img2img函数，并传递修改后的images列表作为参数
                        result = api.img2img(
                            images = temimages,
                            steps = 15,
                            denoising_strength = denoising_strength,
                            cfg_scale = cfg_scale,
                            width = temwidth,
                            height = temheight,
                            prompt = prompt,
                            negative_prompt = negative_prompt,
                        )
                        reply.type = ReplyType.IMAGE
                        b_img = io.BytesIO()
                        result.image.save(b_img, format="PNG")
                        reply.content = b_img
                        e_context["reply"] = reply
                        if os.path.isfile(file_content):
                            os.remove(file_content)
                            logger.info("文件已成功删除")
                        else:
                            logger.error("文件不存在")
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        self.use_number -= 1
                        return
                    else:
                        reply.type = ReplyType.TEXT
                        replyText = f"🥰请先发送图片给我,我将为您进行{role['title']}"
                        reply.content = replyText
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        return
                        
                else:
                    e_context.action = EventAction.CONTINUE  # 事件继续，交付给下个插件或默认逻辑
                    return
            except Exception as e:
                    reply.content = "[pictureChange画图失败] "+str(e)
                    reply = Reply(ReplyType.ERROR, reply.content)
                    logger.error("[pictureChange画图失败] exception: %s" % e)
                    channel._send(reply, e_context["context"])
                    if os.path.isfile(file_content):
                        os.remove(file_content)
                        logger.info("文件已成功删除")
                    if e_context['context'].type == ContextType.IMAGE_CREATE:
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        self.use_number -= 1
                    else:
                        e_context.action = EventAction.CONTINUE  # 事件继续，交付给下个插件或默认逻辑
                        self.use_number -= 1

    def get_help_text(self, **kwargs):
        if not conf().get('image_create_prefix'):
            return "画图功能未启用"
        else:
            trigger = conf()['image_create_prefix'][0]
            help_text = "💨利用百度云和stable-diffusion webui来画图,图生图\n"
            help_text += f"💖使用方法:\n\"{trigger}[关键词1] [关键词2]...:提示语\"的格式作画，如\"{trigger}画高清:男孩，强壮，挺拔，running，黑色耳机，白色短袖（中间有个羊字），黑色头发，黑色短裤\"\n"
            help_text += "🥰目前可用关键词：\n"
            for rule in self.rules:
                keywords = [f"[{keyword}]" for keyword in rule['keywords']]
                help_text += f"{','.join(keywords)}"
                if "desc" in rule:
                    help_text += f"-{rule['desc']}\n"
                else:
                    help_text += "\n"
            help_text += (
                "🥰发送 '一张图片'，我将为您进行图片操作\n"
            )
        return help_text
