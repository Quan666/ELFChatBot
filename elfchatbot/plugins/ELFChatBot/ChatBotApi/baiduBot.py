import asyncio
import hashlib
import json
import re
import uuid
import time
import httpx
from urllib.parse import  quote

import requests


class BaiduBot:
    # api doc https://ai.baidu.com/forum/topic/show/944007
    _api_url = 'https://aip.baidubce.com/rpc/2.0/unit/service/chat'
    _token_url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'
    _API_Key='' # API Key
    _Secret_Key='' # Secret Key
    _bot_id='S3454' # 机器人 ID（S开头）
    _session='10000' # 会话标识（应用内唯一）
    _Proxy = None
    _client = None
    _token=''
    _session_id=''

    async def setSession(self,session):
        self._session=session
    # 获得Token
    async def _getToken(self)->str:
        async with self._client as client:
            # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            res = await client.post(self._token_url.format(self._API_Key,self._Secret_Key))
            # print(res.json())
            return res.json()['access_token']
        pass

    # 发送对话
    async def sendMsg(self,question:str,proxy='')->str:
        params={
            "log_id":re.sub('-','',str(uuid.uuid4())),
            "version":"2.0",
            "service_id":self._bot_id,
            "session_id":self._session_id,
            "request":{
                "query":question,
                "user_id":self._session
            },
            "dialog_state":{
                "contexts":{
                    "SYS_REMEMBERED_SKILLS":[
                        ""
                    ]
                }
            }
        }
        # params={
        #     "bot_session": "",
        #     "log_id": re.sub('-','',str(uuid.uuid4())),
        #     "request": {
        #         "bernard_level": 1,
        #         "query": question,
        #         "query_info": {
        #             "asr_candidates": [],
        #             "source": "KEYBOARD",
        #             "type": "TEXT"
        #         },
        #         "updates": "",
        #         "user_id": self._session
        #     },
        #     "bot_id": self._bot_id,
        #     "version": "2.0"
        # }
        async with self._client as client:
            # headers = {'Content-Type': 'application/x-www-form-urlencoded'},headers=headers
            res = await client.post(self._api_url+'?access_token='+self._token,data=json.dumps(params,ensure_ascii=False))
            data=res.json()
            # print(data)
            self._session_id=data['result']['session_id']
            try:
                # 返回的有多个回答 ，但暂时默认只返回第一个，如果想返回其他的，再下次发送时需把选择的回答放入 bot_session 对话信息发送过去
                # for tmp in data['result']['response_list']:
                #     print(tmp['action_list'][0]['say'])
                #     pass
                return {'code':str(data['error_code']),'session': self._session, 'answer': data['result']['response_list'][0]['action_list'][0]['say']}
            except:
                try:
                    if data['error_code']>292001 or data['error_code']<292015:
                        return {'code':str(data['error_code']),'session': self._session, 'answer': Code['292001~292015']}
                    elif data['error_code']>299001 or data['error_code']<299999:
                        return {'code':str(data['error_code']),'session': self._session, 'answer': Code['299001~299999']}
                    else:
                        return {'code':str(data['error_code']),'session': self._session, 'answer': Code[str(data['error_code'])]}
                except:
                    return {'code':str(data['error_code']),'session': self._session, 'answer': '发生未知错误：'+str(data)}
        pass
    # 初始化
    def __init__(self,API_Key:int,Secret_Key:str,bot_id:str,session:str,proxy:str=None):
        self._API_Key=API_Key
        self._Secret_Key=Secret_Key
        self._bot_id=bot_id
        self._session=session
        if proxy:
            self._Proxy = httpx.Proxy(
                url="http://" + proxy,
                mode="TUNNEL_ONLY"  # May be "TUNNEL_ONLY" or "FORWARD_ONLY". Defaults to "DEFAULT".
            )
            self._client=httpx.AsyncClient(proxies=self._Proxy)
        else:
            self._client=httpx.AsyncClient(proxies={})
        self._token=requests.post(self._token_url.format(self._API_Key,self._Secret_Key)).json()['access_token']
        pass


async def test():
    # 换成你的
    API_Key='fgjfghjasd'
    Secret_Key='dsgdfhg'
    bot_id='S41230'
    session='test2'
    proxy='127.0.0.1:7890'
    bot = BaiduBot(API_Key=API_Key,Secret_Key=Secret_Key,bot_id=bot_id,session=session,proxy=proxy)
    while True:
        msg = await bot.sendMsg(input())
        print(msg)
def startfun():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
if __name__=='__main__':
    startfun()
    pass

Code = {
    '1'	: 'Unknown error	系统繁忙，如果持续出现该错误，请通过QQ群（805312106）或百度Hi群（1617262）联系技术支持团队',
    '2'	: 'Service temporarily unavailable	服务暂不可用，如果持续出现该错误，请通过QQ群（805312106）或百度Hi群（1617262）联系技术支持团队',
    '3'	: 'Unsupported openapi method	调用的API不存在，请检查后重新尝试',
    '4'	: 'Open api request limit reached	集群超限额',
    '6'	: 'No permission to access data	无权限访问该用户数据',
    '17' : 'Open api daily request limit reached	每天请求量超限额，如需更多配额请通过工单系统提交申请',
    '18' : 'Open api qps request limit reached	QPS超限额，如需更多配额请通过工单系统提交申请',
    '19' : 'Open api total request limit reached	请求总量超限额，如需更多配额请通过工单系统提交申请',
    '100' : 'Invalid parameter	无效的access_token参数，请检查后重新尝试',
    '110' : 'Access token invalid or no longer valid	access_token无效',
    '111' : 'Access token expired	access_token过期',
    '282000' : 'Internal error	系统繁忙，如果持续出现该错误，请通过QQ群（805312106）或百度Hi群（1617262）联系技术支持团队',
    '282001' : 'Strategy process failed	系统内部错误，如果持续出现该错误，请通过QQ群（805312106）或百度Hi群（1617262）联系技术支持团队',
    '282004' : 'Parameter[%s] invalid or missing	请求参数格式不正确',
    '282008' : 'The request content type is illegal.	非法请求内容类型',
    '282906' : 'The account cannot use the service	账户请求服务受限，如果持续出现该错误，请通过QQ群（805312106）或百度Hi群（1617262）联系技术支持团队',
    '292001~292015' : '请求参数错误，详见errorMsg字段描述',
    '299001~299999' : '系统繁忙，如果持续出现该错误，请通过QQ群（805312106）或百度Hi群（1617262）联系技术支持团队'
}
