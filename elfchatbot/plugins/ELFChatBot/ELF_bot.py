import re
from typing import Optional

import nonebot
from nonebot import on_command, message
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor, run_postprocessor
from nonebot.rule import to_me, Rule
from nonebot.typing import T_State

from .ChatBotApi import baiduBot
from .ChatBotApi import txbot
from .config import config


def chat_me() -> Rule:
    """
    :说明:

      通过 ``event.is_tome()`` 判断事件是否与机器人有关

    :参数:

      * 无
    """

    async def _chat_me(bot: "Bot", event: "Event", state: T_State) -> bool:

        if str(event.user_id) == str(bot.self_id) or str(event.user_id) in config.txbot:
            return False

        if event.is_tome():
            if event.__getattribute__('message_type') == 'private':
                group_id = None
            else:
                group_id = event.group_id
            try:
                if group_id in config.BanGroup:
                    logger.info('{} 处在黑名单，拒绝回复'.format(group_id))
                    return False
                if event.user_id in config.BanUser:
                    logger.info('{} 处在黑名单，拒绝回复'.format(event.user_id))
                    return False
            except:
                return True
            return True
        else:
            return False

    return Rule(_chat_me)


# nonebot.load_builtin_plugins('single_session') # 有bug
ELF_bot = on_command('', rule=chat_me(), priority=5)


@ELF_bot.handle()
async def handle_first_receive(bot: Bot, event: Event, state: dict):
    if event.__getattribute__('message_type') == 'private':
        group_id = None
    else:
        group_id = event.group_id

    state['group_id'] = group_id
    session = str(event.user_id)

    if group_id is not None:
        await ELF_bot.send('说再见结束聊天~')
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
                await ELF_bot.send('腾讯、百度 闲聊配置出错！请正确配置1')
                return


    except BaseException as e:
        logger.error('腾讯、百度 闲聊配置出错！请正确配置3' + str(e))
        await ELF_bot.send('腾讯、百度 闲聊配置出错！请正确配置3' + str(e))
        return

    args = str(event.message).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if args:
        state["ELF_bot"] = args  # 如果用户发送了参数则直接赋值


@ELF_bot.got("ELF_bot", prompt="")
async def handle_Chat(bot: Bot, event: Event, state: dict):
    if event.__getattribute__('message_type') == 'private':
        group_id = None
    else:
        group_id = event.group_id
    # 临时解决串群问题
    if group_id != state['group_id']:
        if not group_id:
            await ELF_bot.finish('已强制结束其他群组的会话！')
        await ELF_bot.finish()
    msg = state["ELF_bot"]
    if re.search('再见', msg):
        await ELF_bot.send('下次再聊哟！')
        return

    bot = state['Bot']
    r_msg = await bot.sendMsg(msg)

    if group_id is not None:
        res_messages = MessageSegment.at(event.user_id)
    else:
        res_messages = MessageSegment.text('')
    await ELF_bot.reject(res_messages + MessageSegment.text(r_msg['answer']))
