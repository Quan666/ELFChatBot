# ELFChatBot

这是一个闲聊机器人，基于 [Nonebot2](https://v2.nonebot.dev/guide/)
接入了腾讯和百度的闲聊 api

## 申请密钥

1. 腾讯开放平台（推荐作为备用也申请一个）

   前往 [https://ai.qq.com/console/capability/detail/8](https://ai.qq.com/console/capability/detail/8) 注册并创建应用，并在能力库接入 智能闲聊，得到 `app_id` 以及 `app_key`

2. 百度大脑平台（推荐使用！）

   https://ai.baidu.com/unit/home 注册并创建机器人，设置好机器人技能（至少包含闲聊），得到机器人id（S开头）、`api_key`、`secret_key`

   注意：默认优先使用百度

## 部署

**注意：Python 3.7+**

#### 第一次部署

1. 下载代码到本地

2. 参照 [ELF_RSS 2.0的部署方式](https://github.com/Quan666/ELF_RSS/tree/2.0) 

3. 运行 `pip install -r requirements.txt` 

4. 修改插件配置 （文件 `.env` ）

   > 请按照 注释 修改配置文件

   ```bash
   PROXY = '127.0.0.1:7890' # 如果你开启了代理请务必设置此项
   
   # 百度，默认优先使用百度
   baidu_api_key="agdtjhdhd" # API Key
   baidu_secret_key="aqefgshj" # Secret Key
   baidu_bot_id="S065657" # 你闲聊机器人的 id 技能唯一标识，在『我的技能』的技能列表中的技能ID，详情见【请求参数详细说明】
   # 腾讯
   tx_app_id=4631312 # 应用标识（AppId） int
   tx_appkey="asgdhj" # appkey
   ```

5. 运行 `nb run`
6. 收到机器人发送的启动成功消息

#### 从 Nonebot1 到 NoneBot2

1. 卸载 nonebot1

   ```bash
   pip uninstall nonebot
   ```

2. 运行 

   ```
   pip install -r requirements.txt
   ```

3. 参照 `第一次部署`

#### 已经部署过其它 Nonebot2 机器人

1. 下载 项目文件夹 `src/plugins/ELFChatBot` 复制 到你部署好了的机器人 `plugins` 目录
2. 下载 `requirements.txt` 文件，并运行 `pip install -r requirements.txt` 
3. 同 `第一次部署` 一样，修改配置文件
4. 运行 `nb run`


