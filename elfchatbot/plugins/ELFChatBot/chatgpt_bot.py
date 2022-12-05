import re
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, unescape
from nonebot.log import logger
from nonebot.rule import Rule
from nonebot.params import T_State

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


# nonebot.load_builtin_plugins('single_session') # 有bug
ChatGptBot = on_command('chatgpt', rule=chat_me(), priority=1)


@ChatGptBot.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    if event.__getattribute__('message_type') == 'private':
        group_id = None
    else:
        group_id = event.group_id

    state['group_id'] = group_id

    if group_id is not None:
        await ChatGptBot.send(f'说 {config.finish_keyword} 结束聊天~')

    session_token = config.chatgpt_session_token
    if not session_token:
        logger.error("没有配置 ChatGpt session token")
        await ChatGptBot.send("没有配置 ChatGpt session token")
        return
    chatgpt.ChatGPT.global_init(session_token)
    await chatgpt.ChatGPT.refresh_session()
    state['Bot'] = chatgpt.ChatGPT(proxy=config.chat_proxy)

    args = str(event.get_plaintext()).strip()
    if args and args != "chatgpt":
        # 去掉开头的命令
        args = re.sub(r"^chatgpt\s*", "", args)
        state["ChatGptBot"] = args


def remove_cqcode(msg: str) -> str:
    msg = unescape(msg)
    return re.sub('\[.*?\]', '', msg)


@ChatGptBot.got("ChatGptBot", prompt="输入你的问题")
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
    try:
        r_msg = (await bot.sendMsg(msg)).message
    except Exception as e:
        logger.error(e)
        r_msg = f"{e}"

    if group_id is not None:
        res_messages = MessageSegment.at(event.user_id)
    else:
        res_messages = MessageSegment.text('')
    await ChatGptBot.reject(res_messages + MessageSegment.text(r_msg))
