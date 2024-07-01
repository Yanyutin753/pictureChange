from plugins.pictureChange.message import message_reply as MessageReply


class MessageLimit:
    use_number = 0
    wait_number = 0

    def __init__(self):
        pass

    @classmethod
    def isLimit(cls, max_number: int, e_context):
        if cls.use_number + 1 > max_number:
            cls.wait_number += 1
            replyText = f"🧸当前排队人数为 {str(cls.wait_number)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
            MessageReply.reply_Text_Message(True, replyText, e_context)
            return True
        return False

    @classmethod
    def success(cls, max_number: int):
        if cls.use_number > 0:
            cls.use_number -= 1
            if max_number > cls.use_number:
                cls.wait_number = 0
        if cls.wait_number > 0:
            cls.wait_number -= 1

    @classmethod
    def using(cls):
        cls.use_number += 1
