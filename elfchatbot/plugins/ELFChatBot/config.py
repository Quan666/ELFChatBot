import os
from typing import List, Any, Optional

from nonebot import get_driver, logger
from nonebot.config import BaseConfig
from pydantic import AnyHttpUrl, Extra


class BotConfig(BaseConfig):
    class Config:
        extra = Extra.allow

    baidu_api_key: Optional[str] = None  # API Key
    baidu_secret_key: Optional[str] = None  # Secret Key
    # 你闲聊机器人的 id 技能唯一标识，在『我的技能』的技能列表中的技能ID，详情见【请求参数详细说明】
    baidu_bot_id: Optional[str] = None
    # 腾讯
    tx_app_id: Optional[int] = None  # 应用标识（AppId） int
    tx_appkey: Optional[str] = None  # appkey

    opendrandom: bool = False  # 随机回复开关
    randomprobability: int = 1  # 随机回复概率，千分之 1

    bangroup: list = []  # 群组黑名单 示例 [123,123]
    banuser: list = []  # 用户黑名单 示例 [123,123]

    finish_keyword = "再见"  # 支持正则
    chat_proxy: Optional[str] = None  # 代理
    chatgpt_host: Optional[str] = None

    txbot: list = ["2854196306", "2854196310", "2854196320"]  # 腾讯官方机器人

    def __getattr__(self, name: str) -> Any:
        data = self.dict()
        for k, v in data.items():
            if k.casefold() == name.casefold():
                return v
        return None


config = BotConfig(**get_driver().config.dict())
logger.debug(f"BotConfig Config loaded: {config!r}")
