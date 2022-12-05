from typing import Optional
import httpx
import json
import uuid
from pydantic import BaseModel


class ChatGPTMessage(BaseModel):
    message: str
    conversation_id: str
    parent_message_id: str


class ChatGPT:
    authorization: Optional[str] = None
    session_token: str
    proxy: Optional[httpx.Proxy] = None

    conversation_id: Optional[str]
    parent_message_id: str

    @classmethod
    def global_init(cls, session_token: str, authorization: str = None, proxy={}):
        if cls.authorization:
            return

        cls.session_token = session_token
        cls.authorization = authorization
        if proxy:
            cls.proxy = httpx.Proxy(url="http://" + proxy)

    def __init__(self, conversation_id=None, proxy={}):
        self.conversation_id = conversation_id
        self.parent_message_id = self.generate_uuid()

        if proxy:
            self.proxy = httpx.Proxy(url="http://" + proxy)

    def reset_chat(self):
        self.conversation_id = None
        self.parent_message_id = self.generate_uuid()

    @property
    def headers(self):
        return {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.authorization,
            "Content-Type": "application/json",
        }

    def generate_uuid(self):
        uid = str(uuid.uuid4())
        return uid

    async def sendMsg(self, question) -> Optional[ChatGPTMessage]:
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
                "https://chat.openai.com/backend-api/conversation",
                headers=self.headers,
                json=data,
            )
            try:
                response = response.text.splitlines()[-4]
                response = response[6:]
            except:
                raise ValueError(
                    "Response is not in the correct format, response with: "
                    + response.text
                )
        response = json.loads(response)
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
                url="https://chat.openai.com/backend-api/conversation",
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
        s = httpx.AsyncClient(proxies=cls.proxy)
        s.cookies.set("__Secure-next-auth.session-token", cls.session_token)
        response = await s.get("https://chat.openai.com/api/auth/session")
        try:
            cls.session_token = response.cookies.get("__Secure-next-auth.session-token")
            cls.authorization = response.json()["accessToken"]
        except Exception as e:
            raise Exception("Error refreshing session: " + str(e))


if __name__ == "__main__":
    import asyncio

    async def main():
        chat1 = ChatGPT(proxy="127.0.0.1:7890")
        ChatGPT.global_init(
            session_token="",
        )

        chat2 = ChatGPT(proxy="127.0.0.1:7890")
        await ChatGPT.refresh_session()
        print(chat1.authorization)
        print(chat2.authorization)

    asyncio.run(main())
