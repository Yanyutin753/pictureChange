import langid

from bot import bot_factory
from bridge.bridge import Bridge
from common.log import logger


# 翻译提示
def translatePrompt(is_use_fanyi, bot_prompt, prompt, params, session_id):
    if prompt:
        lang = langid.classify(prompt)[0]
        if lang != "en":
            logger.info("[SD] translate prompt from {} to en".format(lang))
            try:
                if not is_use_fanyi:
                    bot = bot_factory.create_bot(Bridge().btype['chat'])
                    session = bot.sessions.build_session(session_id, bot_prompt)
                    session.add_query(prompt)
                    result = bot.reply_text(session)
                    prompt = result['content']
                else:
                    prompt = Bridge().fetch_translate(prompt, to_lang="en")
            except Exception as e:
                logger.info("[SD] translate failed: {}".format(e))
            logger.info("[SD] translated prompt={}".format(prompt))
        params["prompt"] += f", {prompt}"


# 返回翻译提示
def simple_translatePrompt(is_use_fanyi, bot_prompt, prompt, session_id):
    if prompt:
        lang = langid.classify(prompt)[0]
        if lang != "en":
            logger.info("[SD] translate prompt from {} to en".format(lang))
            try:
                if not is_use_fanyi:
                    bot = bot_factory.create_bot(Bridge().btype['chat'])
                    session = bot.sessions.build_session(session_id, bot_prompt)
                    session.add_query(prompt)
                    result = bot.reply_text(session)
                    prompt = result['content']
                else:
                    prompt = Bridge().fetch_translate(prompt, to_lang="en")
                return prompt
            except Exception as e:
                logger.info("[SD] translate failed: {}".format(e))
            logger.info("[SD] translated prompt={}".format(prompt))
        return None
