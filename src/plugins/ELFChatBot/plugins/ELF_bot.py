import re

from nonebot import on_command, message
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.log import logger
from nonebot.rule import to_me, Rule
from nonebot.typing import T_State

from bot import config

from ChatBotApi import baiduBot
from ChatBotApi import txbot

def chat_me() -> Rule:
    """
    :说明:

      通过 ``event.is_tome()`` 判断事件是否与机器人有关

    :参数:

      * 无
    """

    async def _chat_me(bot: "Bot", event: "Event", state: T_State) -> bool:
        if event.is_tome():
            if config.user_list:
                if event.user_id in config.user_list:
                    logger.warning('对话已经存在，不再创建新对话，已抛弃该消息：{}'.format(event))
                    return False
                config.user_list.append(event.user_id)
            else:
                config.user_list=[]
                config.user_list.append(event.user_id)
            return True
        else:
            return False

    return Rule(_chat_me)

# 结束命令时把用户从队列中移除
def stop_chat(user_id):
    if config.user_list:
        config.user_list.remove(user_id)


ELF_bot = on_command('', rule=chat_me(), priority=5)


@ELF_bot.handle()
async def handle_first_receive(bot: Bot, event: Event, state: dict):
    try:
        if event.group_id:
            group_id=event.group_id
    except:
        group_id=None
    state['group_id']=group_id
    try:
        if group_id in config.bangroup:
            stop_chat(user_id=event.user_id)
            return
    except:
        pass
    session=str(event.user_id)
    if group_id is not None:
        await ELF_bot.send('说再见结束聊天~')
        pass
    try:
        API_Key=config.baidu_api_key
        Secret_Key=config.baidu_secret_key
        bot_id=config.baidu_bot_id

        if API_Key==None or Secret_Key == None or bot_id == None:
            logger.error('百度闲聊配置出错！将使用腾讯闲聊！')
            app_id=config.tx_app_id
            appkey=config.tx_appkey
            if app_id == None or appkey == None:
                logger.error('腾讯闲聊配置出错！')
                await ELF_bot.send('腾讯、百度 闲聊配置出错！请正确配置1')
                stop_chat(user_id=event.user_id)
                return
            # 腾讯
            tx = txbot.TXBot(app_id=app_id,appkey=appkey,session=session)
            state['TXBot']=tx
        # 百度
        baidu = baiduBot.BaiduBot(API_Key=API_Key,Secret_Key=Secret_Key,bot_id=bot_id,session=session)
        state['BaiduBot']=baidu

    except BaseException as e:
        await ELF_bot.send('腾讯、百度 闲聊配置出错！请正确配置3'+str(e))
        stop_chat(user_id=event.user_id)
        return

    args = str(event.message).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if args:
        state["ELF_bot"] = args  # 如果用户发送了参数则直接赋值


@ELF_bot.got("ELF_bot", prompt="")
async def handle_Chat(bot: Bot, event: Event, state: dict):
    try:
        if event.group_id:
            group_id=event.group_id
    except:
        group_id=None
    try:
        if group_id in config.bangroup:
            stop_chat(user_id=event.user_id)
            return
    except:
        pass
    msg = state["ELF_bot"]
    if re.search('再见',msg) :
        await ELF_bot.send('下次再聊哟！')
        stop_chat(user_id=event.user_id)
        return
    # 百度
    try:
        baidu = state['BaiduBot']
        r_msg = await baidu.sendMsg(msg)
    except:
        r_msg={}
        r_msg['code']='-1'
    if group_id is not None:
        res_messages = MessageSegment.at(event.user_id)
    else:
        res_messages=MessageSegment.text('')
    if str(r_msg['code'])!='0':
        # 如果出错转为调用腾讯
        logger.error(r_msg)
        try:
            tx = state['TXBot']
            r_msg = await tx.sendMsg(msg)
        except:
            app_id=config.tx_app_id
            appkey=config.tx_appkey
            session=str(event.user_id)
            if app_id == None or appkey == None:
                logger.error('腾讯闲聊配置出错！')
                await ELF_bot.send('腾讯、百度 闲聊配置出错！请正确配置1')
                stop_chat(user_id=event.user_id)
                return
            # 腾讯
            tx = txbot.TXBot(app_id=app_id,appkey=appkey,session=session)
            r_msg = await tx.sendMsg(msg)
        await ELF_bot.reject(res_messages+MessageSegment.text(r_msg['answer']))
    else:
        await ELF_bot.reject(res_messages+MessageSegment.text(r_msg['answer']))