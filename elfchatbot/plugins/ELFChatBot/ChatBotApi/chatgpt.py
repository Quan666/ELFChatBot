import time
from typing import Optional
import httpx
import json
import uuid
from pydantic import BaseModel
import openai


class ChatGPTMessage(BaseModel):
    message: str
    tokens: Optional[int]


class ChatGPT:

    def __init__(self, api_key, proxy={}):
        self.api_key = api_key
        self.systems = []
        self.tokens = 0
        if proxy:
            self.proxy = httpx.Proxy(url="http://" + proxy)
        self.completion = openai.ChatCompletion()
        self.init_chat()

    def init_chat(self):
        self.message_history = []
        if self.systems:
            for s in self.systems:
                self.message_history.append({"role": "system", "content": s})

    def add_system(self, system: str):
        self.systems.append(system)
        self.message_history.append({"role": "system", "content": system})

    async def sendMsg(self, question: str, action: str = "next") -> Optional[ChatGPTMessage]:
        if action not in ["next", "variant"]:
            raise ValueError("action must be 'next' or 'variant'")
        if action == "variant":
            # 移除最后一条消息
            self.message_history.pop()
        else:
            self.message_history.append(
                {"role": "user", "content": question})
        response = self.completion.create(
            model="gpt-3.5-turbo", messages=self.message_history, api_key=self.api_key)
        self.message_history.append(response.choices[0].message)
        self.tokens = response['usage']['total_tokens']
        return ChatGPTMessage(
            message=response.choices[0].message.content,
            tokens=response['usage']['total_tokens'],
        )
