import re

from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent, GroupMessageEvent, unescape
from nonebot.log import logger

tips = '''# 仅在群聊中有效
# 使用方法: @成员1^消息1+消息2+消息3$@成员2^消息1+消息2$
# 其中^到$中间为要发送的消息，用 + 分割'''


fake = on_command('fake', aliases={'伪造'}, priority=5)

@fake.handle()
async def handle_first_receive(bot: Bot, event: MessageEvent, state: dict):
    args = str(event.message).strip()
    if args:
        state["msg"] = args  # 如果用户发送了参数则直接赋值


@fake.got("msg", prompt=tips)
async def handle_RssAdd(bot: Bot, event: MessageEvent, state: dict):
    if not isinstance(event, GroupMessageEvent):
        await fake.send('仅在群聊中有效！')
        return
    msg_info = state["msg"]
    try:
        msg = await fuck_forward(unescape(msg_info), event.group_id, bot)
        await bot.call_api('send_group_forward_msg', group_id=msg['group_id'], messages=msg['messages'])
    except Exception as e:
        await fake.send('参数有误！E: {}'.format(e))
        logger.error('参数有误！E: {}'.format(e))


async def fuck_forward(message, group_id, bot):
    msg = {
        'group_id': group_id,
        'messages': []
    }
    items = re.findall('\[CQ:at,qq=(\d+).*?\].*?\^(.*?)\$', message)
    for qq, content in items:
        user = int(qq)
        try:
            info = await bot.call_api('get_group_member_info', group_id=group_id, user_id=user, no_cache=True)
        except:
            info = await bot.call_api('get_stranger_info', user_id=user, no_cache=True)

        user_name = info.get('card') or info.get('nickname')
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
            msg['messages'].append(node)
    return msg
