import re

import nonebot
from nonebot import on_command
from nonebot.adapters import Event
from nonebot.adapters.cqhttp import Bot, MessageEvent,GroupMessageEvent, unescape
from nonebot.log import logger
from nonebot.rule import to_me


tips='''仅在群聊中有效
使用方法: (@成员1)|(QQ) [自定义昵称]^消息1[+消息2]$[(@成员2)|(QQ) [自定义昵称]^消息1[+消息2]$]
其中^到$中间为要发送的消息，用 + 分割
'''

fake = on_command('fuck', aliases={'伪造','fake'}, rule=to_me(), priority=5)

@fake.handle()
async def handle_first_receive(bot: Bot, event: Event, state: dict):
    # print(event.message_type)
    args = str(event.message).strip()
    if args:
        state["fake"] = args  # 如果用户发送了参数则直接赋值


@fake.got("fake",prompt=tips)
async def handle_fake_msg(bot: Bot, event: Event, state: dict):
    # if event.message_type!='group':
    #     await fake.send('仅在群聊中有效！')
    #     return
    msg_info = state["fake"]
    try:
        msg = await fake_forward(message=unescape(msg_info), group_id=event.group_id,bot=bot,user_id=event.user_id,bot_nofake_id=nonebot.get_driver().config.dict()['superusers'])
        await bot.call_api('send_group_forward_msg',group_id=event.group_id,messages=msg)
        # await fake.send('切勿用作违法！')
    except Exception as e:
        await fake.send('参数有误！E: {}'.format(e))
        logger.error('参数有误！E: {}'.format(e))

# 迫害白名单  设置 user_id bot_nofake_id
async def fake_forward(message:str, group_id:int,bot:Bot,user_id:int=None,bot_nofake_id:set=None)->list:
    msg = []

    items = re.findall('(?:\[CQ:at,qq=)?(\d{5,10})(?:])?(.*?)\^([\s\S]*?)\$', message)
    for qq, name, content in items:
        user = int(qq)
        # 保护 xx 不被迫害
        if bot_nofake_id and str(user) in bot_nofake_id or user in bot_nofake_id:
            user=user_id
        try:
            info = await bot.call_api('get_group_member_info', group_id=group_id, user_id=user, no_cache=True)
        except:
            info = await bot.call_api('get_stranger_info', user_id=user, no_cache=True)

        user_name = name.strip() or info.get('card') or info.get('nickname')
        msg_list = content.split('+')
        for msg_tmp in msg_list:
            node = {
                "type": "node",
                "data": {
                    "name": user_name,
                    "uin": str(user),
                    "content": msg_tmp
                }
            }
            msg.append(node)
        # msg.append({
        #     "type": "node",
        #     "data": {
        #         "name": 'This is fake Message',
        #         "uin": str(user_id),
        #         "content": '！'
        #     }
        # })
    return msg