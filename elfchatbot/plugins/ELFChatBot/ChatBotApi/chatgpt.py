import time
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
    last_refresh = 0

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
        if cls.last_refresh + 60 * 30 > time.time():
            return
        cls.last_refresh = time.time()

        s = httpx.AsyncClient(proxies=cls.proxy)
        s.cookies.set("__Secure-next-auth.session-token", cls.session_token)
        response = await s.get("https://chat.openai.com/api/auth/session")
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
        chat1 = ChatGPT(proxy="127.0.0.1:7890")
        ChatGPT.global_init(
            session_token="eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..3NLgpPg2AtMrszf9.6PGxBZ-GRJKvAYrq1Fy1XQ9irz31x_pwWYbmxaNxuoCqHQA2Tz6MbVmNQvSts8jF64znSI5jU_XtFz0It-tDhnoTjoODCklGLwNTGRn5lfFdBHVHXHQpAM1hiit-CZ6RZfeOmeONUixP98zDzxwXS6kmyQKqnQk0Tq2w2B99Ol-e6_ASan9mW6lEL86x1VaRkfho6Rkb8jQg283uj934Q3alMU-ZNrG6wZvx-TaMJnAuDqddCJ-VYmbYsPeZX-1nrCWpCHsxszl2J8GQRnjVXgow97lez--987SoCbvfREPqgtyH_qWjrQSgYPSq1TAdH4aeSDeR1ozByyUMl3s-B6EAJGYqc9N2asVrFgx9GzurGSNZu2EbjWl1YpNu9R_x-UvJ6HreoS0oGWZkDWYq0fx2LcwQ88g8Xwr-w1XOgU0hqwAH_s2GAmn9reCyYNcbbJfNHQMfTwkQCfFwqpYXifOYLGb4Ed2cMIWMY84yoGWzlFMqDRAfcnL2MKlAO6iEZhVbEoZXh1-_jet0yVPN3ux9wnA4014492ZK4vh7swn9Y4v966aiatiglLYCNfOpjAwCAzGhyUv45w6gq60zByjiYFj4NcOVHHIVlfgLGDfEzbPS202NXWB2wif0ptpch68smEQwIGrBMRD4Ad-2kqCHBsESEMNRKNAU_ZMWBGjSHo9-pF4Tx6Wbeaqxn68SK6Z5jRnR5SQZ0zJKg0z7awqjVz6zUodMT8pWYgsbznZYJL5w6FuS_tm_CRxo1AWmGdMqLeQdEnScvLAbaBLulgv1WOihOMb4aLzYkd1OEnfXQVZWN2OPhfM0jRtOcG_Peq2taDG6jCjRWyvcf4y0AAzPbuoIsKFSbb_brkg9IjGY8JxgFw1oFYz8_tS2ez9cWfDgsl0ZjyZLvpdAELYrZQ8UlN5Zvx15q8HZuTSlW0i2z7D1RaM1weD6RXDagrD81lVa46TUts8QFRpyk9qieGwvLU_K2I8tq-slueVbSnBIocDuXbuXLQYvMUCPJb4aEK7tvpoYRzGYxKdSpnMZEMdxmBtDP5PO4tUph0IswW3dN5aHZW-Z6miry135KqsPUGLqNpZcqptmsQ4pTCyVK2c79aAhkQZfbm8kbe_cAi6cA9LuMwvQhLA4T29I38_5BYeSQBKw3w_vy-5zLSAMVeA7QBNG13TFLnxA6eyArxdXhgNFT5gRbycdNNPz-U2dvn-icAVdnxkadaV0Dnu2ccAnLqidZkcFjbLqacSaL-iRq4nuB_ITWqPphnvQruWtkHnXNQXUdVzGLvzO8O9ZYu5lDWuVRIdSXnqpr4s_U_D-cXcUBw01d9Rr6MpwSSk3CCHYwWLc_hrww6_I2MsCLMj7Cc2ewrN9FG9vLTZzkjz0ryAjwRcWhgtYjUGXAwkFt6Vqt5_EMbu0mbcUHMqKZJ4ORzI3eC63VVbjKPwAV0uY6T1DX0wLc8bZbseNp9V2By_TyIVTZ4TrZWpkDjSxErjFABU_xoCmGS5lZaie9UtCMuYHN4KYTO6IFtHAqZrOyKkv-2bcIeqsbLc4f5_tek-nF4z1SaFEzOUDikdS6jgx3TzJnYmpIe2CSkBTuF5M4pqf-NHsUNLQny168LhY0aQ0S7giabHQBirokk7tGnCXggt7i-0qP0wXuzxl3rLOwOh9wlyOz5YZlt5zlEFNq5TKRMT2b5I9a3C6uSUc8atXBVxPmDaD7SvLG5B8oUlgZ7lyA3vm7obBSS7RjkecPD1W08vi9lfQKukncn_TlHXSdCdnWQ0NZlNq49LsG4dkTWFkqrhdy7fQ3WKY8PntGXmKxUC6jVJqAQNnBetdsClmtgsik1K4GXVvrZnGgmlhYT9onilq9rUenIkM3TQw77y13diYGp1vPY97XGasX8yoLW-o6LdOUjOkq5r1VdHTGbfoOfvLvlDh4mfuxO6CSdVD_xWbF-AfDLNLImmEDO2GFSySyrJ9iBZQEFUauRzckXwdx_bdzvWs_11jIfgx6KyuDO60ta4UVe1_Z9gVUk8aOWe8TDs-NA13Qpo4b26-Akqq1pQIgMskbUX5C1RR4k61Pc6Ob4cP7pmM_Q1dDmNJmVPFVkLOk8mK7q04MRZs1_6FUeMD37xPxhDVNS5H3Fz4Rckv-Xtg8yGfQJjOszH8dsgOqOiLRSH07p5pS5-e9MwMZvaDYe75DGm1AWa25cFdD8Cle54D3xG0Ouv519KtWS88SbjyTySynJXQFqn0BnTba_xZAQFoiZjOP8DHD3uMlQ2fT_j3MHOxYBVZExhTNIE.7LcW3_W2_u6QEODUCJg02Q",
        )

        chat2 = ChatGPT(proxy="127.0.0.1:7890")
        await ChatGPT.refresh_session()
        await ChatGPT.refresh_session()
        await ChatGPT.refresh_session()
        print(chat1.authorization)
        print(chat2.authorization)

    asyncio.run(main())
