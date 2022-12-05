import re
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, unescape
from nonebot.log import logger
from nonebot.rule import Rule
from nonebot.params import T_State

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
            if event.__getattribute__("message_type") == "private":
                group_id = None
            else:
                group_id = event.group_id
            try:
                if group_id in config.bangroup:
                    logger.info("{} 处在黑名单，拒绝回复".format(group_id))
                    return False
                if event.user_id in config.banuser:
                    logger.info("{} 处在黑名单，拒绝回复".format(event.user_id))
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
ELF_bot = on_command("", rule=chat_me(), priority=5)


@ELF_bot.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    if event.__getattribute__("message_type") == "private":
        group_id = None
    else:
        group_id = event.group_id

    state["group_id"] = group_id
    session = str(event.user_id)

    if group_id is not None:
        await ELF_bot.send(f"说 {config.finish_keyword} 结束聊天~")
    try:
        API_Key = config.baidu_api_key
        Secret_Key = config.baidu_secret_key
        bot_id = config.baidu_bot_id

        app_id = config.tx_app_id
        appkey = config.tx_appkey

        if API_Key and Secret_Key and bot_id:
            state["Bot"] = baiduBot.BaiduBot(
                API_Key=API_Key, Secret_Key=Secret_Key, bot_id=bot_id, session=session
            )
        else:
            logger.error("百度闲聊配置出错！将使用腾讯闲聊！")
            if app_id and appkey:
                state["Bot"] = txbot.TXBot(
                    app_id=app_id, appkey=appkey, session=session
                )
            else:
                logger.error("腾讯、百度 闲聊配置出错！请正确配置1！")
                await ELF_bot.send("腾讯、百度 闲聊配置出错！请正确配置1")
                return

    except BaseException as e:
        logger.error("腾讯、百度 闲聊配置出错！请正确配置3" + str(e))
        await ELF_bot.send("腾讯、百度 闲聊配置出错！请正确配置3" + str(e))
        return

    args = str(event.get_plaintext()).strip()
    if args:
        state["ELF_bot"] = args


def remove_cqcode(msg: str) -> str:
    msg = unescape(msg)
    return re.sub("\[.*?\]", "", msg)


@ELF_bot.got("ELF_bot", prompt="")
async def handle_Chat(bot: Bot, event: Event, state: T_State):
    if event.__getattribute__("message_type") == "private":
        group_id = None
    else:
        group_id = event.group_id

    # 临时解决串群问题
    if group_id != state["group_id"]:
        if not group_id:
            await ELF_bot.finish("已强制结束其他群组的会话！")
        await ELF_bot.finish()
    msg = remove_cqcode(str(state["ELF_bot"]))
    if len(msg) <= 0:
        await ELF_bot.reject()
    if re.search(config.finish_keyword, msg):
        await ELF_bot.send("下次再聊哟！")
        return

    bot = state["Bot"]
    r_msg = await bot.sendMsg(msg)

    if group_id is not None:
        res_messages = MessageSegment.at(event.user_id)
    else:
        res_messages = MessageSegment.text("")
    await ELF_bot.reject(res_messages + MessageSegment.text(r_msg["answer"]))
