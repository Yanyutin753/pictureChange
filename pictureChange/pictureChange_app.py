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
from enum import Enum
from bot import bot_factory
from bridge.bridge import Bridge


@plugins.register(name="pictureChange", desc="利用百度云AI和stable-diffusion webui来画图,图生图", version="1.8.3",
                  author="yangyang")
class pictureChange(Plugin):
    # 定义了模型枚举类型  需要填入自己的模型，有几个填几个
    class Model(Enum):
        MODEL_1 = "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
        MODEL_2 = "absolutereality_v181.safetensors [463d6a9fe8]"
        MODEL_3 = "QteaMix-fp16.safetensors [0c1efcbbd6]"

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
                self.host = config["start"]["host"]
                self.port = config["start"]["port"]
                self.use_https = config["start"]["use_https"]
                self.request_bot_name = config["request_bot_name"]
                self.file_url = config["file_url"]
                self.other_user_id = config["use_group"]
                self.is_use_fanyi = config["is_use_fanyi"]
                self.bot_prompt = '''作为 Stable Diffusion Prompt 提示词专家，您将从关键词中创建提示，通常来自 Danbooru 
                等数据库。提示通常描述图像，使用常见词汇，按重要性排列，并用逗号分隔。避免使用"-"或"."，但可以接受空格和自然语言。避免词汇重复。为了强调关键词，请将其放在括号中以增加其权重。例如，"( 
                flowers)"将'flowers'的权重增加1.1倍，而"(((flowers)))"将其增加1.331倍。使用"( 
                flowers:1.5)"将'flowers'的权重增加1.5倍。只为重要的标签增加权重。提示包括三个部分：前缀（质量标签+风格词+效果器）+ 主题（图像的主要焦点）+ 
                场景（背景、环境）。前缀影响图像质量。像"masterpiece"、"best 
                quality"、"4k"这样的标签可以提高图像的细节。像"illustration"、"lensflare"这样的风格词定义图像的风格。像"bestlighting"、"lensflare 
                "、"depthoffield"这样的效果器会影响光照和深度。主题是图像的主要焦点，如角色或场景。对主题进行详细描述可以确保图像丰富而详细。增加主题的权重以增强其清晰度。对于角色，描述面部、头发、身体、服装、姿势等特征。场景描述环境。没有场景，图像的背景是平淡的，主题显得过大。某些主题本身包含场景（例如建筑物、风景）。像"花草草地"、"阳光"、"河流"这样的环境词可以丰富场景。你的任务是设计图像生成的提示。请按照以下步骤进行操作：我会发送给您一个图像场景。生成详细的图像描述，输出 Positive Prompt ,并确保用英文回复我。示例：我发送：二战时期的护士。 您回复：A WWII-era nurse in a German uniform, holding a wine bottle and stethoscope, sitting at a table in white attire, with a table in the background, masterpiece, best quality, 4k, illustration style, best lighting, depth of field, detailed character, detailed environment. '''
                try:
                    self.max_number = config["max_number"]
                except KeyError:
                    self.max_number = 3
                try:
                    self.max_size = config["max_size"]
                except KeyError:
                    self.max_size = 1150
                self.use_pictureChange = config["use_pictureChange"]
                try:
                    if self.use_https:
                        response = requests.get(f"https://{self.host}:{self.port}")
                    else:
                        response = requests.get(f"http://{self.host}:{self.port}")
                    if response.status_code != 200:
                        self.use_pictureChange = False
                        print("由于sd没开启self.use_pictureChange变为", False)
                except requests.exceptions.RequestException as e:
                    print("连接错误:", e)
                    self.use_pictureChange = False
                    print("由于连接错误，self.use_pictureChange变为", False)

                self.use_number = 0
                self.out_number = 0
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[pictureChange] inited")
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                logger.warn(f"[SD] init failed, {config_path} not found.")
            else:
                logger.warn("[SD] init failed.")
            raise e

    def on_handle_context(self, e_context: EventContext):
        reply = Reply()
        start_time = time.time()  # 记录开始时间
        temimages = []
        api = webuiapi.WebUIApi(**self.start_args)
        # if e_context['context'].type != ContextType.IMAGE_CREATE:
        #     return
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
        prompt = "masterpiece, best quality, "
        negative_prompt = ""
        title = ""
        roleRule_options = {}
        channel = e_context["channel"]
        cmsg: ChatMessage = e_context['context']['msg']
        session_id = cmsg.from_user_id
        for role in self.role_options:
            if content.startswith(role['title'] + " "):
                title = role['title']
                denoising_strength = role['denoising_strength']
                cfg_scale = role['cfg_scale']
                prompt += role['prompt']
                negative_prompt += role['negative_prompt']
                if "options" in role:
                    for key in role["options"]:
                        roleRule_options[key] = role["options"][key]
                check_exist = True
                break
        try:
            if e_context['context'].type == ContextType.IMAGE:
                if self.use_pictureChange == False:
                    reply.type = ReplyType.TEXT
                    replyText = f"😭图生图关闭了，快联系小羊管理员开启图生图吧🥰🥰🥰"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return
                elif self.use_number >= self.max_number:
                    self.out_number += 1
                    reply.type = ReplyType.TEXT
                    replyText = f"🧸当前排队人数为 {str(self.out_number)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return
                else:
                    self.use_number += 1
                    msg.prepare()
                    reply.type = ReplyType.TEXT
                    file_content_encoded = urllib.parse.quote(file_content)
                    role_2 = urllib.parse.quote("🤖 图像修复")
                    role_3 = urllib.parse.quote("❎ 暂不处理")
                    replyText = f"🥰 点击或输入指令\n✨ 让我为您进行图片操作\n\n✅ 支持指令"
                    replyText += "\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={} {}\">{}</a>".format(
                        role_2, file_content_encoded, "🤖 图像修复")
                    for role in self.role_options:
                        role_title_encoded = urllib.parse.quote(role['title'])
                        replyText += "\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={} {}\">{}</a>".format(
                            role_title_encoded, file_content_encoded, role['title'])
                    replyText += "\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={} {}\">{}</a>".format(
                        role_3, file_content_encoded, "❎ 暂不处理")
                    replyText += f"\n\n🎡 自定义 {file_content} MODEL_1 [关键词] 例如 黑色头发 白色短袖 等关键词"
                    replyText += "\n\n🥰 温馨提示\n👑 MODEL_1 : 动漫\n🏆 MODEL_2 : 现实\n🧩 MODEL_3 : Q版"
                    replyText += "\n\n🚀 发送指令后，请耐心等待一至两分钟！\n💖 感谢您的使用！"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return

            elif any(ext in content for ext in ["jpg", "jpeg", "png", "gif", "webp"]) and (
                    content.startswith("http://") or content.startswith("https://")):
                if self.use_pictureChange == False:
                    reply.type = ReplyType.TEXT
                    replyText = f"😭图生图关闭了，快联系小羊管理员开启图生图吧🥰🥰🥰"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return
                elif self.use_number >= self.max_number:
                    self.out_number += 1
                    reply.type = ReplyType.TEXT
                    replyText = f"🧸当前排队人数为 {str(self.out_number)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
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
                    file_content_encoded = urllib.parse.quote(file_content)
                    role_2 = urllib.parse.quote("🤖 图像修复")
                    role_3 = urllib.parse.quote("❎ 暂不处理")
                    replyText = f"🥰 点击或输入指令\n✨ 让我为您进行图片操作\n\n✅ 支持指令"
                    replyText += "\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={} {}\">{}</a>".format(
                        role_2, file_content_encoded, "🤖 图像修复")
                    for role in self.role_options:
                        role_title_encoded = urllib.parse.quote(role['title'])
                        replyText += "\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={} {}\">{}</a>".format(
                            role_title_encoded, file_content_encoded, role['title'])
                    replyText += "\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={} {}\">{}</a>".format(
                        role_3, file_content_encoded, "❎ 暂不处理")
                    replyText += f"\n\n🎡 自定义 {file_content} MODEL_1 [关键词] 例如 黑色头发 白色短袖 等关键词"
                    replyText += "\n\n🥰 温馨提示\n👑 MODEL_1 : 动漫\n🏆 MODEL_2 : 现实\n🧩 MODEL_3 : Q版"
                    replyText += "\n\n🚀 发送指令后，请耐心等待一至两分钟！\n💖 感谢您的使用！"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return

            elif e_context['context'].type == ContextType.IMAGE_CREATE:
                if self.use_pictureChange == False:
                    reply.content = f"😭SD画图关闭了，快联系小羊管理员开启SD画图吧🥰🥰🥰"
                    reply = Reply(ReplyType.ERROR, reply.content)
                    channel._send(reply, e_context["context"])
                    e_context.action = EventAction.CONTINUE  # 事件继续，交付给下个插件或默认逻辑
                    return
                elif self.use_number >= self.max_number:
                    self.out_number += 1
                    reply.type = ReplyType.TEXT
                    replyText = f"🧸当前排队人数为 {str(self.out_number)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
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
                        reply.content = self.get_help_text(verbose=True)
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
                                    if not self.is_use_fanyi:
                                        btype = Bridge().btype['chat']
                                        bot = bot_factory.create_bot(Bridge().btype['chat'])
                                        session = bot.sessions.build_session(session_id, self.bot_prompt)
                                        session.add_query(prompt)
                                        result = bot.reply_text(session)
                                        prompt = result['content']
                                    else:
                                        prompt = Bridge().fetch_translate(prompt, to_lang="en")
                                except Exception as e:
                                    logger.info("[SD] translate failed: {}".format(e))
                                logger.info("[SD] translated prompt={}".format(prompt))
                            params["prompt"] += f", {prompt}"
                        if len(options) > 0:
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

                        model = options["sd_model_checkpoint"]
                        modelname = ""
                        for member in self.Model:
                            if model == member.value:
                                modelname = member.name
                                break
                        else:
                            print("使用了其他模型")

                        # 发送图片
                        b_img = io.BytesIO()
                        result.image.save(b_img, format="PNG")
                        reply.content = b_img
                        reply = Reply(ReplyType.IMAGE, reply.content)
                        channel._send(reply, e_context["context"])

                        # 发送放大和转换指令
                        reply.type = ReplyType.TEXT
                        all_seeds = result.info['all_seeds']
                        end_time = time.time()  # 记录结束时间
                        elapsed_time = end_time - start_time  # 计算经过的时间

                        minutes = int(elapsed_time // 60)  # 计算分钟数
                        seconds = int(elapsed_time % 60)  # 计算秒数

                        reply.content = f"🔥 图片创作成功!\n⏱ 图片处理耗时：{minutes}分钟 {seconds}秒\n🧸点击指令，我将为您进行图片操作！\n\n✅ 支持指令"
                        temposition_1 = 0
                        temposition_2 = 0
                        for seed in all_seeds:
                            temposition_1 += 1
                            if temposition_1 % 2 == 0:
                                reply.content += "\t\t"
                            else:
                                reply.content += "\n\n"
                            reply.content += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent=🔍 放大 {}.png\">{}</a>".format(
                                f"txt2img-images/{seed}", f"🤖 放大 {temposition_1}")
                        for seed in all_seeds:
                            temposition_2 += 1
                            if temposition_2 % 2 == 0:
                                reply.content += "\t\t"
                            else:
                                reply.content += "\n\n"
                            reply.content += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent=🎡 变换 {}.png {}\">{}</a>".format(
                                f"txt2img-images/{seed}", modelname, f"🎡 变换 {temposition_2}")
                        reply.content += "\n\n🥰 温馨提示\n✨ 1:左上 2:右上 3:左下 4:右下\n👑 MODEL_1 : 动漫\n🏆 MODEL_2 : 现实\n🧩 MODEL_3 : Q版\n🌈 图片不满意的话，点击变换\n🐏 小羊帮你再画一幅吧!\n💖 感谢您的使用！"
                        reply.content = reply.content
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                        self.use_number -= 1
                        self.out_number = 0

                        return

            elif content.startswith("🤖 图像修复 "):
                if self.use_pictureChange == False:
                    reply.type = ReplyType.TEXT
                    replyText = f"😭图生图关闭了，快联系小羊管理员开启图生图吧🥰🥰🥰"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return
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
                    token_params = {"grant_type": "client_credentials", "client_id": self.API_KEY,
                                    "client_secret": self.SECRET_KEY}
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

                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            self.use_number -= 1
                            self.out_number = 0

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
                    replyText = "🥰图片已成功删除\n🧸感谢您的使用！"
                else:
                    replyText = "😭文件不存在或已删除"
                reply.content = replyText
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                self.use_number -= 1
                self.out_number = 0

                return

            elif content.startswith("🎡 自定义 "):
                if self.use_pictureChange == False:
                    reply.type = ReplyType.TEXT
                    replyText = f"😭图生图关闭了，快联系小羊管理员开启图生图吧🥰🥰🥰"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return

                parts = content.split(" ")
                # 提取所需内容
                # 文件
                file_content = parts[2]
                # 所用模型
                sdModel = getattr(self.Model, parts[3]).value
                # 拿到关键字
                keywords_start_index = content.index("[关键词]") + len("[关键词]")
                keywords = content[keywords_start_index:].strip()
                # 使用逗号连接关键词
                prompt = ", ".join(keywords.split())
                lang = langid.classify(prompt)[0]
                if lang != "en":
                    # 非英文，进行翻译
                    logger.info("[SD] Translating prompt from {} to en".format(lang))
                    try:
                        if not self.is_use_fanyi:
                            btype = Bridge().btype['chat']
                            bot = bot_factory.create_bot(Bridge().btype['chat'])
                            session = bot.sessions.build_session(session_id, self.bot_prompt)
                            session.add_query(prompt)
                            result = bot.reply_text(session)
                            prompt = result['content']
                        else:
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
                    image = Image.open(io.BytesIO(image_data))
                    width, height = image.size
                    temwidth = width
                    temheight = height
                    if temwidth < 768 or temheight < 768:
                        if temwidth < temheight:
                            temheight = 768 * (temheight / temwidth)
                            temwidth = 768
                        else:
                            temwidth = 768 * (temwidth / temheight)
                            temheight = 768
                    if temwidth > 1024 or temheight > 1024:
                        if temwidth < temheight:
                            temwidth = 1024 * (temwidth / temheight)
                            temheight = 1024
                        else:
                            temheight = 1024 * (temheight / temwidth)
                            temwidth = 1024
                    text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n----------\n💨图宽:{int(temwidth)} 图高:{int(temheight)}\n✨感谢您的耐心与支持"
                    temreply = Reply(ReplyType.TEXT, text)
                    channel._send(temreply, e_context["context"])
                    # 将PIL Image对象添加到images列表中
                    temimages.append(image)
                    default_options = {
                        "sd_model_checkpoint": sdModel
                    }
                    api.set_options(default_options)
                    # 调用img2img函数，并传递修改后的images列表作为参数
                    result = api.img2img(
                        images=temimages,
                        steps=20,
                        denoising_strength=0.6,
                        cfg_scale=7.0,
                        batch_size=4,
                        n_iter=1,
                        do_not_save_samples=True,
                        do_not_save_grid=True,
                        save_images=True,
                        width=temwidth,
                        height=temheight,
                        prompt=prompt,
                        negative_prompt="(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure,",

                    )

                    # 发送图片
                    b_img = io.BytesIO()
                    result.image.save(b_img, format="PNG")
                    reply.content = b_img
                    reply = Reply(ReplyType.IMAGE, reply.content)
                    channel._send(reply, e_context["context"])

                    # 发送放大和转换指令
                    reply.type = ReplyType.TEXT
                    all_seeds = result.info['all_seeds']
                    end_time = time.time()  # 记录结束时间
                    elapsed_time = end_time - start_time  # 计算经过的时间
                    minutes = int(elapsed_time // 60)  # 计算分钟数
                    seconds = int(elapsed_time % 60)  # 计算秒数
                    reply.content = f"🔥 图片创作成功!\n⏱ 图片处理耗时：{minutes}分钟 {seconds}秒\n🧸点击指令，我将为您进行图片操作！\n\n✅ 支持指令"
                    temposition_1 = 0
                    temposition_2 = 0
                    for seed in all_seeds:
                        temposition_1 += 1
                        if temposition_1 % 2 == 0:
                            reply.content += "\t\t"
                        else:
                            reply.content += "\n\n"
                        reply.content += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent=🔍 放大 {}.png\">{}</a>".format(
                            f"img2img-images/{seed}", f"🤖 放大 {temposition_1}")
                    for seed in all_seeds:
                        temposition_2 += 1
                        if temposition_2 % 2 == 0:
                            reply.content += "\t\t"
                        else:
                            reply.content += "\n\n"
                        reply.content += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent=🎡 变换 {}.png {}\">{}</a>".format(
                            f"img2img-images/{seed}", parts[3], f"🎡 变换 {temposition_2}")
                    reply.content += "\n\n🥰 温馨提示\n✨ 1:左上 2:右上 3:左下 4:右下\n👑 MODEL_1 : 动漫\n🏆 MODEL_2 : 现实\n🧩 MODEL_3 : Q版\n🌈 图片不满意的话，点击变换\n🐏 小羊帮你再画一幅吧!\n💖 感谢您的使用！"
                    reply.content = reply.content
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    self.use_number -= 1
                    self.out_number = 0

                    return
                else:
                    reply.type = ReplyType.TEXT
                    replyText = f"🥰请先发送图片给我,我将为您进行{role['title']}"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return

            elif content.startswith("🔍 放大 "):
                if self.use_pictureChange == False:
                    reply.content = f"😭pictureChange插件被管理员关闭了\n快联系小羊管理员开启pictureChange插件吧🥰🥰🥰"
                    reply = Reply(ReplyType.ERROR, reply.content)
                    channel._send(reply, e_context["context"])
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return
                else:
                    try:
                        file_content = content[len("🔍 放大 "):]
                        if self.use_https:
                            image_url = "https://{}:{}/{}{}".format(self.host, self.port, self.file_url,
                                                                    file_content)
                        else:
                            image_url = "http://{}:{}/{}{}".format(self.host, self.port, self.file_url,
                                                                   file_content)
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            text = f"🚀放大图片生成中～～～\n⏳请您耐心等待1-2分钟\n✨请稍等片刻✨✨\n❤️感谢您的耐心与支持"
                            temreply = Reply(ReplyType.TEXT, text)
                            channel._send(temreply, e_context["context"])
                            reply.type = ReplyType.IMAGE_URL
                            reply.content = image_url
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                            return
                        else:
                            reply.type = ReplyType.TEXT
                            reply.content = "[😭放大图片失败]\n❌图片只会保存一天\n😂图片可能已被删除\n🥰快联系小羊解决问题吧！"
                            e_context["reply"] = reply
                            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    except Exception as e:
                        reply.type = ReplyType.TEXT
                        reply.content = "[😭放大图片失败]" + str(e) + "❌图片只会保存一天\n😂图片可能已被删除\n🥰快联系小羊解决问题吧！"
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑


            elif content.startswith("🎡 变换 "):
                if self.use_pictureChange == False:
                    reply.content = f"😭pictureChange插件被管理员关闭了\n快联系小羊管理员开启pictureChange插件吧🥰🥰🥰"
                    reply = Reply(ReplyType.ERROR, reply.content)
                    channel._send(reply, e_context["context"])
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return
                elif self.use_number >= self.max_number:
                    self.out_number += 1
                    reply.type = ReplyType.TEXT
                    replyText = f"🧸当前排队人数为 {str(self.out_number)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return
                else:
                    file_content = content.split()[2]
                    sdModel = getattr(self.Model, content.split()[3]).value
                    if self.use_https:
                        image_url = "https://{}:{}/{}{}".format(self.host, self.port, self.file_url,
                                                                file_content)
                    else:
                        image_url = "http://{}:{}/{}{}".format(self.host, self.port, self.file_url,
                                                               file_content)
                    # 发送 GET 请求获取图像数据
                    response = requests.get(image_url)
                    # 检查响应状态码是否为 200，表示请求成功
                    if response.status_code == 200:
                        # 获取图像的二进制数据
                        image_data = response.content

                        # 将二进制图像数据转换为 PIL Image 对象
                        image = Image.open(io.BytesIO(image_data))
                        width, height = image.size
                        temwidth = width
                        temheight = height
                        if width < self.max_size or height < self.max_size:
                            temwidth = 1.05 * width
                            temheight = 1.05 * height
                        text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n----------\n💨图宽:{int(temwidth)} 图高:{int(temheight)}\n✨感谢您的耐心与支持"
                        temreply = Reply(ReplyType.TEXT, text)
                        channel._send(temreply, e_context["context"])
                        # 将PIL Image对象添加到images列表中
                        temimages.append(image)
                        default_options = {
                            "sd_model_checkpoint": sdModel
                        }
                        api.set_options(default_options)
                        # 调用img2img函数，并传递修改后的images列表作为参数
                        result = api.img2img(
                            images=temimages,
                            steps=20,
                            denoising_strength=0.6,
                            cfg_scale=7.0,
                            batch_size=4,
                            n_iter=1,
                            do_not_save_samples=True,
                            do_not_save_grid=True,
                            save_images=True,
                            width=temwidth,
                            height=temheight,
                            prompt=prompt,
                            negative_prompt="(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure,",

                        )
                        # 发送图片
                        b_img = io.BytesIO()
                        result.image.save(b_img, format="PNG")
                        reply.content = b_img
                        reply = Reply(ReplyType.IMAGE, reply.content)
                        channel._send(reply, e_context["context"])

                        # 发送放大和转换指令
                        reply.type = ReplyType.TEXT
                        all_seeds = result.info['all_seeds']
                        end_time = time.time()  # 记录结束时间
                        elapsed_time = end_time - start_time  # 计算经过的时间
                        minutes = int(elapsed_time // 60)  # 计算分钟数
                        seconds = int(elapsed_time % 60)  # 计算秒数
                        reply.content = f"🔥 图片转化成功!\n⏱ 图片处理耗时：{minutes}分钟 {seconds}秒\n🧸点击指令，我将为您进行图片操作！\n\n✅ 支持指令"
                        temposition_1 = 0
                        temposition_2 = 0
                        for seed in all_seeds:
                            temposition_1 += 1
                            if temposition_1 % 2 == 0:
                                reply.content += "\t\t"
                            else:
                                reply.content += "\n\n"
                            reply.content += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent=🔍 放大 {}.png\">{}</a>".format(
                                f"img2img-images/{seed}", f"🤖 放大 {temposition_1}")
                        for seed in all_seeds:
                            temposition_2 += 1
                            if temposition_2 % 2 == 0:
                                reply.content += "\t\t"
                            else:
                                reply.content += "\n\n"
                            reply.content += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent=🎡 变换 {}.png {}\">{}</a>".format(
                                f"img2img-images/{seed}", content.split()[3], f"🎡 变换 {temposition_2}")
                        reply.content += "\n\n"
                        reply.content += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent=🎡 变换 {} {}\">{}</a>".format(
                            f"{file_content}", content.split()[3], f"🎡 变换 原图")
                        reply.content += "\n\n🥰 温馨提示\n✨ 1:左上 2:右上 3:左下 4:右下\n👑 MODEL_1 : 动漫\n🏆 MODEL_2 : 现实\n🧩 MODEL_3 : Q版\n🌈 图片不满意的话，点击变换\n🐏 小羊帮你再画一幅吧!\n💖 感谢您的使用！"
                        reply.content = reply.content
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

                    else:
                        reply.type = ReplyType.TEXT
                        reply.content = "[😭转换图片失败]\n快联系小羊解决问题吧🥰🥰🥰"
                        e_context["reply"] = reply
                        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

                    self.use_number -= 1
                    self.out_number = 0

                    return



            elif check_exist:
                if self.use_pictureChange == False:
                    reply.type = ReplyType.TEXT
                    replyText = f"😭图生图关闭了，快联系小羊管理员开启图生图吧🥰🥰🥰"
                    reply.content = replyText
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    return
                file_content = content[len(title + " "):]
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
                    image = Image.open(io.BytesIO(image_data))
                    width, height = image.size
                    temwidth = width
                    temheight = height
                    if temwidth < 768 or temheight < 768:
                        if temwidth < temheight:
                            temheight = 768 * (temheight / temwidth)
                            temwidth = 768
                        else:
                            temwidth = 768 * (temwidth / temheight)
                            temheight = 768
                    if temwidth > 1024 or temheight > 1024:
                        if temwidth < temheight:
                            temwidth = 1024 * (temwidth / temheight)
                            temheight = 1024
                        else:
                            temheight = 1024 * (temheight / temwidth)
                            temwidth = 1024

                    text = f"🚀图片生成中～～～\n⏳请您耐心等待1-2分钟\n----------\n💨图宽:{int(temwidth)} 图高:{int(temheight)}\n✨感谢您的耐心与支持"
                    temreply = Reply(ReplyType.TEXT, text)
                    channel._send(temreply, e_context["context"])

                    # 将PIL Image对象添加到images列表中
                    temimages.append(image)
                    options = {**self.default_options, **roleRule_options}
                    # 更改固定模型
                    api.set_options(options)
                    # 调用img2img函数，并传递修改后的images列表作为参数
                    result = api.img2img(
                        images=temimages,
                        steps=20,
                        denoising_strength=denoising_strength,
                        cfg_scale=cfg_scale,
                        width=temwidth,
                        height=temheight,
                        batch_size=4,
                        n_iter=1,
                        do_not_save_samples=True,
                        do_not_save_grid=True,
                        save_images=True,
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                    )

                    model = options["sd_model_checkpoint"]
                    modelname = ""
                    for member in self.Model:
                        if model == member.value:
                            modelname = member.name
                            break
                    else:
                        print("使用了其他模型")

                    # 发送图片
                    b_img = io.BytesIO()
                    result.image.save(b_img, format="PNG")
                    reply.content = b_img
                    reply = Reply(ReplyType.IMAGE, reply.content)
                    channel._send(reply, e_context["context"])
                    # 发送放大和转换指令
                    reply.type = ReplyType.TEXT
                    all_seeds = result.info['all_seeds']
                    end_time = time.time()  # 记录结束时间
                    elapsed_time = end_time - start_time  # 计算经过的时间
                    minutes = int(elapsed_time // 60)  # 计算分钟数
                    seconds = int(elapsed_time % 60)  # 计算秒数
                    reply.content = f"🔥 图片转化成功!\n⏱ 图片处理耗时：{minutes}分钟 {seconds}秒\n🧸点击指令，我将为您进行图片操作！\n\n✅ 支持指令"
                    temposition_1 = 0
                    temposition_2 = 0
                    for seed in all_seeds:
                        temposition_1 += 1
                        if temposition_1 % 2 == 0:
                            reply.content += "\t\t"
                        else:
                            reply.content += "\n\n"
                        reply.content += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent=🔍 放大 {}.png\">{}</a>".format(
                            f"img2img-images/{seed}", f"🤖 放大 {temposition_1}")
                    for seed in all_seeds:
                        temposition_2 += 1
                        if temposition_2 % 2 == 0:
                            reply.content += "\t\t"
                        else:
                            reply.content += "\n\n"
                        reply.content += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent=🎡 变换 {}.png {}\">{}</a>".format(
                            f"img2img-images/{seed}", modelname, f"🎡 变换 {temposition_2}")
                    reply.content += "\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={} {}\">{}</a>".format(
                        title, file_content, "🎡 变换 原图")
                    reply.content += "\n\n🥰 温馨提示\n✨ 1:左上 2:右上 3:左下 4:右下\n👑 MODEL_1 : 动漫\n🏆 MODEL_2 : 现实\n🧩 MODEL_3 : Q版\n🌈 图片不满意的话，点击变换\n🐏 小羊帮你再画一幅吧!\n💖 感谢您的使用！"
                    reply.content = reply.content
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                    self.use_number -= 1
                    self.out_number = 0

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
            reply.content = "[😭pictureChange画图失败] " + str(e) + "\n快联系小羊解决问题吧🥰🥰🥰"
            reply = Reply(ReplyType.ERROR, reply.content)
            logger.error("[pictureChange画图失败] exception: %s" % e)
            channel._send(reply, e_context["context"])
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
            self.use_number -= 1
            self.out_number = 0

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
