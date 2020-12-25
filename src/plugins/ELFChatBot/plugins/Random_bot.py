import random
import re

from nonebot import on_message
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.log import logger
from nonebot.rule import to_me
from bot import config

from ChatBotApi import baiduBot
from ChatBotApi import txbot

if config.opendrandom:
    Random_bot = on_message(rule=None, permission=None, handlers=None, temp=False, priority=1, block=True, state=None)
    @Random_bot.handle()
    async def handle_first_receive(bot: Bot, event: Event, state: dict):

        r = random.randint(0,1000)
        print(r)
        if float(r)>=float(config.randomprobability)*10:
            return
        session=str(event.user_id)
        if not event.group_id: # 只在群组生效
            return
        try:
            if event.group_id in config.bangroup:
                return
        except:
            pass
        try:
            proxy=config.proxy
            try:
                if len(proxy)<1:
                    proxy=None
            except:
                proxy=None
            API_Key=config.baidu_api_key
            Secret_Key=config.baidu_secret_key
            bot_id=config.baidu_bot_id

            if API_Key==None or Secret_Key == None or bot_id == None:
                logger.error('百度闲聊配置出错！将使用腾讯闲聊！')
                app_id=config.tx_app_id
                appkey=config.tx_appkey
                if app_id == None or appkey == None:
                    logger.error('腾讯、百度 闲聊配置出错！请正确配置1')
                    return
                # 腾讯
                tx = txbot.TXBot(app_id=app_id,appkey=appkey,session=session,proxy=proxy)
                state['TXBot']=tx
            # 百度
            baidu = baiduBot.BaiduBot(API_Key=API_Key,Secret_Key=Secret_Key,bot_id=bot_id,session=session,proxy=proxy)
            state['BaiduBot']=baidu

        except BaseException as e:
            logger.error('腾讯、百度 闲聊配置出错！请正确配置3'+str(e))

        args = str(event.message).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
        if args:
            state["Random_bot"] = args  # 如果用户发送了参数则直接赋值


    @Random_bot.got("Random_bot", prompt="")
    async def handle_Chat(bot: Bot, event: Event, state: dict):
        try:
            if event.group_id in config.bangroup:
                return
        except:
            pass
        msg = state["Random_bot"]
        # 百度
        try:
            baidu = state['BaiduBot']
            r_msg = await baidu.sendMsg(msg)
        except:
            r_msg={}
            r_msg['code']='-1'

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
                proxy=config.proxy
                if app_id == None or appkey == None:
                    logger.error('腾讯、百度 闲聊配置出错！请正确配置1')
                    # await Random_bot.send('腾讯、百度 闲聊配置出错！请正确配置1')
                    return
                # 腾讯
                tx = txbot.TXBot(app_id=app_id,appkey=appkey,session=session,proxy=proxy)
                r_msg = await tx.sendMsg(msg)
            await Random_bot.send(r_msg['answer'],)
        else:
            await Random_bot.send(r_msg['answer'])