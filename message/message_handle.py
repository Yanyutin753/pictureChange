# 用于初始化消息
from channel.chat_message import ChatMessage


# 初始化消息
def init_content(e_context):
    context = e_context['context']
    msg: ChatMessage = context["msg"]
    msg.prepare()
    return context.content.strip()
