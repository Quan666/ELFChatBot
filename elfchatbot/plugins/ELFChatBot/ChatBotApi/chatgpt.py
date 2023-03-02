from typing import Optional
import httpx
from pydantic import BaseModel
import httpx
import traceback

HOST = "api.openai.com"


class ChatGPTMessage(BaseModel):
    message: str
    tokens: Optional[int]


class ChatGPT:

    def __init__(self, api_key, proxy={}, host=HOST):
        self.host = host
        self.api_key = api_key
        self.systems = []
        self.tokens = 0
        if proxy:
            self.proxy = httpx.Proxy(url="http://" + proxy)
        else:
            self.proxy = {}
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
        try:
            async with httpx.AsyncClient(proxies=self.proxy) as client:
                response = await client.post(
                    f"https://{self.host}/v1/chat/completions",
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": self.message_history,
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    timeout=120
                )
                response = response.json()
                response["choices"][0]["message"]["content"] = response["choices"][0]["message"]["content"].strip()
                self.message_history.append(response["choices"][0]["message"])
                self.tokens = response['usage']['total_tokens']
                return ChatGPTMessage(
                    message=response["choices"][0]["message"]["content"].strip(),
                    tokens=response['usage']['total_tokens'],
                )
        except Exception as e:
            traceback.print_exc()
            return ChatGPTMessage(
                message=f"发生错误：{e}",
                tokens=0,
            )
