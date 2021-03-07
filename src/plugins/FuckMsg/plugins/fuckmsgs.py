import nonebot
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.rule import to_me
import re
from nonebot.log import logger

fuck = on_command('fucks', aliases={'伪造s','fakes'}, rule=to_me(), priority=5)

@fuck.handle()
async def handle_first_receive(bot: Bot, event: Event, state: dict):
    if not event.group_id:
        await fuck.send('仅在群聊中有效！')
        return
    args = str(event.message).strip()
    state['fake_messages']=[]
    if args:
        state["fuck"] = args  # 如果用户发送了参数则直接赋值

@fuck.got("fuck", prompt="使用方法: (QQ号)|(@某人) [自定义昵称]%第一条消息[~第二条消息]\n% 后表示消息\n消息用 ~ 分割\n切勿用作违法！\n输入要伪造的消息(发送“结束伪造”结束)：")
async def handle_Chat(bot: Bot, event: Event, state: dict):
    if not event.group_id:
        await fuck.send('仅在群聊中有效！')
        return
    state['get_group_id']=event.group_id
    msg_info = state["fuck"]
    if re.search('结束伪造',msg_info):
        if state['fake_messages']:
            await bot.call_api('send_group_forward_msg',group_id=event.group_id,messages=state['fake_messages'])
            # await fuck.send('切勿用作违法！')
        return
    else:
        try:
            msgs_list=await fuck_forward(msg_info, event.group_id,bot,event.user_id)
            for msg_tmp in msgs_list:
                state['fake_messages'].append(msg_tmp)
        except Exception as e:
            await fuck.send('参数有误！E: {}'.format(e))
            logger.error('参数有误！E: {}'.format(e))
        await fuck.reject('')




# 仅仅在群聊中有效
# 触发：(bot昵称)|(@bot) fuck
# 使用方法: (QQ号)|(@某人) [自定义昵称]%第一条消息[~第二条消息]
# % 后表示消息
# 消息用 ~ 分割
async def fuck_forward(message, group_id,bot,user_id=None):
    msg = []
    message = message.replace("&amp;", "&") \
        .replace("&#91;", "[") \
        .replace("&#93;", "]") \
        .replace("&#44;", ",")
    message_list = message.split('%',1)
    contents = re.findall('^(?:\[CQ:at,qq=)?(\d{5,})(?:])?([^|]+)?', message_list[0]) #=([^|]+)(?:\|)?$

    for con in contents:
        user=int(con[0])
        if int(con[0]) in nonebot.get_driver().config.dict()['superusers']:
            user=user_id
        try:
            info = await bot.call_api('get_group_member_info',group_id=group_id,user_id=user,no_cache=True)
        except:
            info=await bot.call_api('get_stranger_info',user_id=user,no_cache=True)
        if not con[1].strip() or con[1]=='':
            nickname=info['nickname']
            try:
                if info['card']:
                    nickname=info['card']
            except:
                pass
        else:
            nickname=con[1].strip()
        content = message_list[1]
        msg_list = content.split('~')
        for msg_tmp in msg_list:
            node = {"type": "node",
                "data": {"name": nickname,
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
    if msg:
        return msg
    else:
        return None