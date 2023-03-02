import re
from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, unescape
from nonebot.log import logger
from nonebot.rule import Rule
from nonebot.params import T_State
from nonebot.permission import SUPERUSER

from .ChatBotApi import chatgpt
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
                if group_id in config.bangroup:
                    logger.info('{} 处在黑名单，拒绝回复'.format(group_id))
                    return False
                if event.user_id in config.banuser:
                    logger.info('{} 处在黑名单，拒绝回复'.format(event.user_id))
                    return False
                if re.search(config.finish_keyword, str(event.get_plaintext()).strip()):
                    return False
            except:
                return True
            return True
        else:
            return False

    return Rule(_chat_me)


PRIVATE_API_KEY = {
    # "user_id":"api_key"
}

ChatGptBot = on_command('chatgpt', rule=chat_me(), priority=5)


@ChatGptBot.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    if event.__getattribute__('message_type') == 'private':
        group_id = None
    else:
        group_id = event.group_id

    state['group_id'] = group_id

    # 获取用户的 api_key
    if str(event.user_id) in PRIVATE_API_KEY:
        api_key = PRIVATE_API_KEY[str(event.user_id)]
    else:
        api_key = PRIVATE_API_KEY.get('default', None)

    if api_key is None:
        await ChatGptBot.finish('请先设置 api_key\n私聊发送：\nchatgpt_api_key xxxxxx')

    await ChatGptBot.send(f'ChatGPT聊天模式\n#预设\n#重试(重新回答)\n#刷新(重置上下文)\n说 {config.finish_keyword} 结束聊天~')
    args = str(event.get_plaintext()).strip()
    if args and args != "chatgpt":
        # 去掉开头的命令
        args = re.sub(r"^chatgpt\s*", "", args)
        state["ChatGptBot"] = args
    state['Bot'] = chatgpt.ChatGPT(
        api_key=api_key, proxy=config.chat_proxy)


def remove_cqcode(msg: str) -> str:
    msg = unescape(msg)
    return re.sub('\[.*?\]', '', msg)


@ChatGptBot.got("ChatGptBot")
async def handle_Chat(bot: Bot, event: Event, state: T_State):
    if event.__getattribute__('message_type') == 'private':
        group_id = None
    else:
        group_id = event.group_id

    # 临时解决串群问题
    if group_id != state['group_id']:
        if not group_id:
            await ChatGptBot.finish('已强制结束其他群组的会话！')
        await ChatGptBot.finish()
    msg = remove_cqcode(str(state["ChatGptBot"]))
    if len(msg) <= 0:
        await ChatGptBot.reject()
    if re.search(config.finish_keyword, msg):
        await ChatGptBot.send('下次再聊哟！')
        return

    bot = state['Bot']

    if msg == '#刷新':
        bot.reset_chat()
        await ChatGptBot.reject('已刷新上下文, 请重新输入问题')

    if msg.startswith('#预设'):
        bot.add_system(msg[3:].strip())
        await ChatGptBot.reject('已添加预设指令, 请重新输入问题')

    try:
        if msg == '#重试':
            r_msg = (await bot.sendMsg(question=msg, action="variant")).message
        else:
            r_msg = (await bot.sendMsg(msg)).message
    except Exception as e:
        logger.error(e)
        r_msg = f"{e}"

    if group_id is not None:
        res_messages = MessageSegment.at(event.user_id)
    else:
        res_messages = MessageSegment.text('')
    await ChatGptBot.reject(res_messages + MessageSegment.text(r_msg))


ChatGptBotToken = on_command(
    'chatgpt_api_key', rule=chat_me(), priority=5)


@ChatGptBotToken.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_plaintext()).strip()
    api_key = re.sub(r"^chatgpt_api_key\s*", "", args)
    if not api_key:
        await ChatGptBotToken.finish('没有输入 api_key')
    PRIVATE_API_KEY[str(event.user_id)] = api_key

    await ChatGptBotToken.finish('api_key 设置成功')


ChatGptBotTokenAdmin = on_command(
    'chatgpt_api_key_admin', rule=chat_me(), priority=5, permission=SUPERUSER)


@ChatGptBotTokenAdmin.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_plaintext()).strip()
    api_key = re.sub(r"^chatgpt_api_key_admin\s*", "", args)
    if not api_key:
        PRIVATE_API_KEY["default"] = None
        await ChatGptBotToken.finish('全局 api_key 已清除')
    PRIVATE_API_KEY["default"] = api_key

    await ChatGptBotToken.finish('全局 api_key 设置成功')
