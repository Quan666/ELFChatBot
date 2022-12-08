import time
from typing import Optional
import httpx
import json
import uuid
from pydantic import BaseModel
# from OpenAIAuth.OpenAIAuth import OpenAIAuth
# import threading

HOST = "https://chat.openai.com"


class ChatGPTMessage(BaseModel):
    message: str
    conversation_id: str
    parent_message_id: str


class ChatGPT:
    authorization: Optional[str] = None
    session_token: Optional[str] = None
    proxy: Optional[httpx.Proxy] = None
    last_refresh = 0
    host: str = HOST

    # auth: Optional[OpenAIAuth] = None
    # login_lock = threading.Lock()

    conversation_id: Optional[str]
    parent_message_id: str

    @classmethod
    def global_init(cls, session_token: str, authorization: str = None, proxy={}, host=HOST):
        if cls.authorization:
            return

        cls.session_token = session_token
        cls.authorization = authorization
        if proxy:
            cls.proxy = httpx.Proxy(url="http://" + proxy)
        cls.host = host

    # @classmethod
    # def global_login(cls, username: str, password: str, proxy={}):
    #     use_proxy = False
    #     if proxy:
    #         proxy = "http://" + proxy
    #         use_proxy = True
    #     cls.auth = OpenAIAuth(username, password,
    #                           proxy=proxy, use_proxy=use_proxy)

    #     cls.login()

    # @classmethod
    # def login(cls):
    #     def _login():
    #         try:
    #             cls.auth.begin()
    #         except Exception as e:
    #             print(e)
    #     if cls.auth:
    #         with cls.login_lock:
    #             # new thread
    #             task = threading.Thread(target=_login)
    #             task.start()
    #             # 等待线程结束
    #             task.join()
    #             cls.session_token = cls.auth.session_token

    def __init__(self, conversation_id=None, proxy={}):
        self.conversation_id = conversation_id
        self.parent_message_id = self.generate_uuid()
        self.last_request_data = None

        if proxy:
            self.proxy = httpx.Proxy(url="http://" + proxy)

    def reset_chat(self):
        self.conversation_id = None
        self.parent_message_id = self.generate_uuid()
        self.last_request_data = None

    @property
    def headers(self):
        if not self.authorization:
            raise ValueError("Authorization is not set")
        return {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.authorization,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }

    def generate_uuid(self):
        uid = str(uuid.uuid4())
        return uid

    async def sendMsg(self, question: str, action: str = "next") -> Optional[ChatGPTMessage]:
        if action not in ["next", "variant"]:
            raise ValueError("action must be 'next' or 'variant'")
        if action == "variant" and self.last_request_data:
            data = self.last_request_data
            data["action"] = "variant"
        else:
            data = {
                "action": "next",
                "messages": [
                    {
                        "id": str(self.generate_uuid()),
                        "role": "user",
                        "content": {"content_type": "text", "parts": [question]},
                    }
                ],
                "conversation_id": self.conversation_id,
                "parent_message_id": self.parent_message_id,
                "model": "text-davinci-002-render",
            }

        async with httpx.AsyncClient(proxies=self.proxy, timeout=60 * 3) as client:
            response = await client.post(
                f"{self.host}/backend-api/conversation",
                headers=self.headers,
                json=data,
            )
            try:
                response = response.text.splitlines()[-4]
                response = response[6:]
            except:
                # if response.status_code == 401:
                #     self.login()
                #     await self.sendMsg(question, action)
                if response.text.find("Too Many Requests") != -1:
                    return ChatGPTMessage(message="请求太快，休息会", conversation_id="", parent_message_id="")
                elif response.text.find("token_expired") != -1:
                    return ChatGPTMessage(message="Token 过期请重置", conversation_id="", parent_message_id="")
                raise ValueError(
                    "Response is not in the correct format, response with: "
                    + response.text
                )
        response = json.loads(response)
        if action != "variant":
            self.last_request_data = data
            self.last_request_data["conversation_id"] = response["conversation_id"]

        self.parent_message_id = response["message"]["id"]
        self.conversation_id = response["conversation_id"]
        message = response["message"]["content"]["parts"][0]
        return ChatGPTMessage(
            message=message,
            conversation_id=self.conversation_id,
            parent_message_id=self.parent_message_id,
        )

    async def sendMsgStream(self, question):
        data = {
            "action": "next",
            "messages": [
                {
                    "id": str(self.generate_uuid()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [question]},
                }
            ],
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_message_id,
            "model": "text-davinci-002-render",
        }
        async with httpx.AsyncClient(proxies=self.proxy, timeout=60 * 3) as client:
            response = await client.stream(
                method="POST",
                url=f"{self.host}/backend-api/conversation",
                headers=self.headers,
                json=data,
            )
            for line in response.iter_lines():
                try:
                    line = line.decode("utf-8")
                    if line == "":
                        continue
                    line = line[6:]
                    line = json.loads(line)
                    try:
                        message = line["message"]["content"]["parts"][0]
                    except:
                        continue
                    yield message
                except:
                    continue

    @classmethod
    async def refresh_session(cls):
        if cls.last_refresh + 60 * 30 > time.time():
            return
        cls.last_refresh = time.time()

        s = httpx.AsyncClient(proxies=cls.proxy)
        s.cookies.set("__Secure-next-auth.session-token", cls.session_token)
        response = await s.get(f"{cls.host}/api/auth/session", headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        })
        try:
            cls.session_token = response.cookies.get(
                "__Secure-next-auth.session-token")
            cls.authorization = response.json().get("accessToken", cls.authorization)

        except Exception as e:
            raise Exception(
                f"Error refreshing session: {str(e)} {response.text}")


if __name__ == "__main__":
    import asyncio

    async def main():
        chat1 = ChatGPT()
        ChatGPT.global_init(
            session_token=""
        )

        await ChatGPT.refresh_session()
        print(chat1.authorization)
        print(await chat1.sendMsg("你将成为可爱的女朋友"))
        print(await chat1.sendMsg("你将成为可爱的女朋友", action="variant"))
    asyncio.run(main())
