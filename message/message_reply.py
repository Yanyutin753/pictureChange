from bridge.reply import ReplyType, Reply
from common.log import logger
from plugins import EventAction


# 根据reply_type,reply_content发送消息类型
# 根据is_break决定是否结束会话
def reply_message(is_break, reply_type, reply_content, e_context):
    reply = Reply()
    reply.type = reply_type
    reply.content = reply_content
    e_context["reply"] = reply
    e_context.action = EventAction.BREAK_PASS if is_break else EventAction.CONTINUE
    return e_context


# 根据reply_content发送文本消息
# 根据is_break决定是否结束会话
def reply_Text_Message(is_break, reply_content, e_context):
    reply_message(is_break, ReplyType.TEXT, reply_content, e_context)


# 根据reply_content发送错误文本消息
# 根据is_break决定是否结束会话
def reply_Error_Message(is_break, reply_content, e_context):
    logger.error(reply_content)
    reply_message(is_break, ReplyType.ERROR, reply_content, e_context)


# 根据reply_content(image_url)获取图片,发送图片消息
# 根据is_break决定是否结束会话
def reply_Image_Url_Message(is_break, reply_content, e_context):
    reply_message(is_break, ReplyType.IMAGE_URL, reply_content, e_context)


# 根据reply_content(图片文件二进制)发送音频消息
# 根据is_break决定是否结束会话
def reply_Image_Message(is_break, reply_content, e_context):
    reply_message(is_break, ReplyType.IMAGE, reply_content, e_context)


# 根据reply_content(音频文件二进制)发送音频消息
# 根据is_break决定是否结束会话
def reply_Video_Message(is_break, reply_content, e_context):
    reply_message(is_break, ReplyType.VIDEO, reply_content, e_context)


# 根据reply_content(video_url)获取音频,发送音频消息
# 根据is_break决定是否结束会话
def reply_Video_Url_Message(is_break, reply_content, e_context):
    reply_message(is_break, ReplyType.VIDEO_URL, reply_content, e_context)


# 立即发送文本消息(reply_content)，不结束会话
def tem_reply_Text_Message(reply_content, e_context):
    reply = Reply(ReplyType.TEXT, reply_content)
    e_context['channel'].send(reply, e_context["context"])


# 立即发送图片消息(reply_content)，不结束会话
def tem_reply_Image_Message(reply_content, e_context):
    reply = Reply(ReplyType.IMAGE, reply_content)
    e_context['channel'].send(reply, e_context["context"])


# 立即发送图片消息(reply_content)，不结束会话
def tem_reply_Image_Url_Message(reply_content, e_context):
    reply = Reply(ReplyType.IMAGE_URL, reply_content)
    e_context['channel'].send(reply, e_context["context"])


# 立即发送音频消息(reply_content)，不结束会话
def tem_reply_Video_Message(reply_content, e_context):
    try:
        reply = Reply(ReplyType.FILE, reply_content)
        e_context['channel'].send(reply, e_context["context"])
    except Exception as e:
        logger.error(f"Error sending video: {e}")


# 立即发送音频消息(reply_content)，不结束会话
def tem_reply_Video_Url_Message(reply_content, e_context):
    reply = Reply(ReplyType.VIDEO_URL, reply_content)
    e_context['channel'].send(reply, e_context["context"])
