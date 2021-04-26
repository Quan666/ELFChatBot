import random
import re

from nonebot import on_message
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, unescape
from nonebot.log import logger
from nonebot.rule import Rule
from nonebot.typing import T_State

from .ChatBotApi import baiduBot
from .ChatBotApi import txbot
from .config import config


def remove_cqcode(msg: str) -> str:
    msg = unescape(msg)
    return re.sub('\[.*?\]','',msg)

def chat_random() -> Rule:
    """
    :说明:



    :参数:

      * 无
    """

    async def _chat_random(bot: "Bot", event: "Event", state: T_State) -> bool:

        if event.__getattribute__('message_type') == 'private':
            return False

        if str(event.user_id) == str(bot.self_id) or str(event.user_id) in config.txbot:
            return False

        r = random.randint(0, 1000)
        if float(r) >= float(config.randomprobability) * 10:
            return False
        try:
            if event.group_id in config.bangroup or event.user_id in config.BanUser:
                logger.info('{} 处在黑名单，拒绝回复'.format(event.group_id))
                return False
            if event.user_id in config.banuser:
                logger.info('{} 处在黑名单，拒绝回复'.format(event.user_id))
                return False
        except:
            return True
        return True

    return Rule(_chat_random)


if config.opendrandom:
    Random_bot = on_message(rule=chat_random(), permission=None, priority=10)


    @Random_bot.handle()
    async def handle_first_receive(bot: Bot, event: Event, state: dict):
        args = remove_cqcode(str(event.message).strip())
        if len(args)<=0:
            return
        session = str(event.user_id)

        try:
            API_Key = config.baidu_api_key
            Secret_Key = config.baidu_secret_key
            bot_id = config.baidu_bot_id

            app_id = config.tx_app_id
            appkey = config.tx_appkey

            if API_Key and Secret_Key and bot_id:
                state['Bot'] = baiduBot.BaiduBot(API_Key=API_Key, Secret_Key=Secret_Key, bot_id=bot_id, session=session)
            else:
                logger.error('百度闲聊配置出错！将使用腾讯闲聊！')
                if app_id and appkey:
                    state['Bot'] = txbot.TXBot(app_id=app_id, appkey=appkey, session=session)
                else:
                    logger.error('腾讯、百度 闲聊配置出错！请正确配置1！')
                    return
        except BaseException as e:
            logger.error('腾讯、百度 闲聊配置出错！请正确配置3' + str(e))
            return

        r_msg = await state['Bot'].sendMsg(args)
        await Random_bot.finish(MessageSegment.text(r_msg['answer']))
