import asyncio
import hashlib
import json
import re
import uuid
import time
import httpx
from urllib.parse import  quote


class TXBot:
    # api doc https://ai.qq.com/doc/nlpchat.shtml
    _api_url = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat'
    _app_id=1000001 # 应用标识（AppId） int
    _appkey='' # appkey
    _time_stamp=1493468759 # 请求时间戳（秒级） int
    _nonce_str='fa577ce340859f9fe' # 随机字符串
    _sign='' #签名信息
    _session='10000' # 会话标识（应用内唯一）
    _question='你叫啥' # 用户输入的聊天内容
    _Proxy = None
    _client = None
    async def setSession(self,session):
        self._session=session
    # 计算接口签名
    async def _getSign(self,params:dict)->str:
        params= sorted(params.items(), key=lambda d:d[0], reverse = False)
        tmp=''
        for key,value in params:
            tmp+=str(key)+'='+quote(str(value))+'&'
        tmp+='app_key='+str(self._appkey)
        return await self._md5(tmp)
        pass

    # 发送对话
    async def sendMsg(self,question:str)->str:
        params={
            'app_id':self._app_id,
            'time_stamp':int(time.time()),
            'nonce_str':re.sub('-','',str(uuid.uuid4())),
            'session':self._session,
            'question':question
        }
        sign = await self._getSign(params=params)
        params['sign']=sign
        async with self._client as client:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            res = await client.post(self._api_url,headers=headers,params=params)
            data=res.json()
            if data['ret'] != 0:
                try:
                    return {'code':str(data['ret']),'session': self._session, 'answer': Code[str(data['ret'])]}
                except:
                    return {'code':str(data['ret']),'session': self._session, 'answer': '发生未知错误：'+str(data)}
            return {'code':str(data['ret']),'session': self._session, 'answer': data['data']['answer']}
        pass

    async def _md5(self,str:str)->str:
        m = hashlib.md5()
        m.update(str.encode("utf8"))
        return m.hexdigest().upper()
    # 初始化
    def __init__(self,app_id:int,appkey:str,session:str,proxy:str=None):
        self._app_id=app_id # 应用标识（AppId） int
        self._appkey=appkey # appkey
        self._session=session # 会话标识（应用内唯一）
        if proxy:
            self._Proxy = httpx.Proxy(
                url="http://" + proxy,
                mode="TUNNEL_ONLY"  # May be "TUNNEL_ONLY" or "FORWARD_ONLY". Defaults to "DEFAULT".
            )
            self._client=httpx.AsyncClient(proxies=self._Proxy)
        else:
            self._client=httpx.AsyncClient(proxies={})
        pass


async def test():
    # 换成你的
    app_id=000000000
    appkey='WhSI06tq'
    session='404'
    proxy='127.0.0.1:7890'
    bot = TXBot(app_id=app_id,appkey=appkey,session=session,proxy=proxy)
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
    '9': 'qps超过限制:用户认证升级或者降低调用频率',
    '4096': '参数非法:请检查请求参数是否符合要求',
    '12289': '应用不存在:请检查app_id是否有效的应用标识（AppId）',
    '12801': '素材不存在:请检查app_id对应的素材模版id',
    '12802': '素材ID与应用ID不匹配:请检查app_id对应的素材模版id',
    '16385': '缺少app_id参数:请检查请求中是否包含有效的app_id参数',
    '16386': '缺少time_stamp参数:请检查请求中是否包含有效的time_stamp参数',
    '16387': '缺少nonce_str参数:请检查请求中是否包含有效的nonce_str参数',
    '16388': '请求签名无效:请检查请求中的签名信息（sign）是否有效',
    '16389': '缺失API权限:请检查应用是否勾选当前API所属接口的权限',
    '16390': 'time_stamp参数无效:请检查time_stamp距离当前时间是否超过5分钟',
    '16391': '同义词识别结果为空:请尝试更换文案',
    '16392': '专有名词识别结果为空:请尝试更换文案',
    '16393': '意图识别结果为空:请尝试更换文案',
    '16394': '闲聊返回结果为空:请联系开发人员反馈问题',
    '16396': '图片格式非法:请检查图片格式是否符合API要求',
    '16397': '图片体积过大:请检查图片大小是否超过API限制',
    '16402': '图片没有人脸:请检查图片是否包含人脸',
    '16403': '相似度错误:请联系开发人员反馈问题',
    '16404': '人脸检测失败:请联系开发人员反馈问题',
    '16405': '图片解码失败:请联系开发人员反馈问题',
    '16406': '特征处理失败:请联系开发人员反馈问题',
    '16407': '提取轮廓错误:请联系开发人员反馈问题',
    '16408': '提取性别错误:请联系开发人员反馈问题',
    '16409': '提取表情错误:请联系开发人员反馈问题',
    '16410': '提取年龄错误:请联系开发人员反馈问题',
    '16411': '提取姿态错误:请联系开发人员反馈问题',
    '16412': '提取眼镜错误:请联系开发人员反馈问题',
    '16413': '提取魅力值错误:请联系开发人员反馈问题',
    '16414': '语音合成失败:请联系开发人员反馈问题',
    '16415': '图片为空:请检查图片是否正常',
    '16416': '个体已存在:请检查个体是否已存在',
    '16417': '个体不存在:请检查个体是否不存在',
    '16418': '人脸不存在:请检查人脸是否不存在',
    '16419': '分组不存在:请检查分组是否不存在',
    '16420': '分组列表不存在:请检查分组列表是否不存在',
    '16421': '人脸个数超过限制:请检查是否超过系统限制',
    '16422': '个体个数超过限制:请检查是否超过系统限制',
    '16423': '组个数超过限制:请检查是否超过系统限制',
    '16424': '对个体添加了几乎相同的人脸:请检查个体已添加的人脸',
    '16425': '无效的图片格式:请检查图片格式是否符号API要求',
    '16426': '图片模糊度检测失败:请联系开发人员反馈问题',
    '16427': '美食图片检测失败:请联系开发人员反馈问题',
    '16428': '提取图像指纹失败:请联系开发人员反馈问题',
    '16429': '图像特征比对失败:请联系开发人员反馈问题',
    '16430': 'OCR照片为空:请检查待处理图片是否为空',
    '16431': 'OCR识别失败:请尝试更换带有文字的图片',
    '16432': '输入图片不是身份证:请检查图片是否为身份证',
    '16433': '名片无足够文本:请检查名片是否正常',
    '16434': '名片文本行倾斜角度太大:请检查名片是否正常',
    '16435': '名片模糊:请检查名片是否正常',
    '16436': '名片姓名识别失败:请尝试更换姓名显示清晰的名片图片',
    '16437': '名片电话识别失败:请尝试更换电话显示清晰的名片图片',
    '16438': '图像为非名片图像:请尝试更换有效的名片图片',
    '16439': '检测或者识别失败:请联系开发人员反馈问题',
    '16440': '未检测到身份证:请对准边框(避免拍摄时倾角和旋转角过大、摄像头)',
    '16441': '请使用第二代身份证件进行扫描:请使用第二代身份证进行处理',
    '16442': '不是身份证正面照片:请使用带证件照的一面进行处理',
    '16443': '不是身份证反面照片:请使用身份证反面进行进行处理',
    '16444': '证件图片模糊:请确保证件图片清晰',
    '16445': '请避开灯光直射在证件表面:请避开灯光直射在证件表面',
    '16446': '行驾驶证OCR识别失败:请尝试更换有效的行驾驶证图片',
    '16447': '通用OCR识别失败:请尝试更换带有文字的图片',
    '16448': '银行卡OCR预处理错误:请联系开发人员反馈问题',
    '16449': '银行卡OCR识别失败:请尝试更换有效的银行卡图片',
    '16450': '营业执照OCR预处理失败:请联系开发人员反馈问题',
    '16451': '营业执照OCR识别失败:请联系开发人员反馈问题',
    '16452': '意图识别超时:请联系开发人员反馈问题',
    '16453': '闲聊处理超时:请联系开发人员反馈问题',
    '16454': '语音识别解码失败:请检查语音参数是否正确编码',
    '16455': '语音过长或空:请检查语音参数是否正确编码或者长度是否合法',
    '16456': '翻译引擎失败:请联系开发人员反馈问题',
    '16457': '不支持的翻译类型:请检查翻译类型参数是否合法',
    '16460': '输入图片与识别场景不匹配:请检查场景参数是否正确，所传图片与场景是否匹配',
    '16461': '识别结果为空:当前图片无法匹配已收录的标签，请尝试更换图片',
    '16462': '多人脸检测识别结果为空:图片中识别不出人脸，请尝试更换图片',
    '16467': '跨年龄人脸识别出错:请尝试更换有人脸的图片',
    '16468': '跨年龄人脸识别结果为空:源图片与目标图片中识别不出匹配的人脸，请尝试更换图片',
    '16472': '音频鉴黄识别出错:请确保音频地址能正常下载音频，尝试更换音频'
}
