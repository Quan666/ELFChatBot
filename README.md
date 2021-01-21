# ELFChatBot

> **这是一个闲聊机器人，基于 [Nonebot2](https://v2.nonebot.dev/guide/)**  
> **接入了腾讯和百度的闲聊 api，百度的api支持连续对话**  
> **可以实现群聊、私聊，同时随机回复群聊消息。**  


效果图：

![image-20210114125523902](https://cdn.jsdelivr.net/gh/Quan666/CDN/pic/image-20210114125523902.png)

## 娱乐功能
  1. 随机回复群友消息
  2. 伪造转发合并消息（fake、fakes触发，具体使用看代码）

## 申请密钥

1. 腾讯开放平台（推荐作为备用也申请一个）

   前往 [https://ai.qq.com/console/capability/detail/8](https://ai.qq.com/console/capability/detail/8) 注册并创建应用，并在能力库接入 智能闲聊，得到 `app_id` 以及 `app_key`

2. 百度大脑平台（推荐使用！）

   https://ai.baidu.com/unit/home 注册并创建机器人，设置好机器人技能（至少包含闲聊），得到机器人id（S开头）、`api_key`、`secret_key`

   注意：默认优先使用百度

## 部署

**注意：Python 3.7+**

### 一 、配置 QQ 协议端

   目前支持的协议有:

   - [OneBot(CQHTTP)](https://github.com/howmanybots/onebot/blob/master/README.md)

   QQ 协议端举例:

   - [go-cqhttp ](https://github.com/Mrs4s/go-cqhttp)(基于 [MiraiGo ](https://github.com/Mrs4s/MiraiGo))
   - [cqhttp-mirai-embedded](https://github.com/yyuueexxiinngg/cqhttp-mirai/tree/embedded)
   - [Mirai ](https://github.com/mamoe/mirai)+ [cqhttp-mirai](https://github.com/yyuueexxiinngg/cqhttp-mirai)
   - [Mirai ](https://github.com/mamoe/mirai)+ [Mirai Native ](https://github.com/iTXTech/mirai-native)+ [CQHTTP](https://github.com/richardchien/coolq-http-api)
   - [OICQ-http-api ](https://github.com/takayama-lily/onebot)(基于 [OICQ](https://github.com/takayama-lily/oicq))

   这里以 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)为例

   1. 下载 go-cqhttp 对应平台的 release 文件，[点此前往](https://github.com/Mrs4s/go-cqhttp/releases)

   2. 运行 exe 文件或者使用 `./go-cqhttp` 启动

   3. 生成默认配置文件并修改默认配置

       ```json
      {
        "uin": 你的QQ号,
        "password": "你的密码",
        "encrypt_password": false,
        "password_encrypted": "",
        "enable_db": true,
        "access_token": "",
        "relogin": {
          "enabled": true,
          "relogin_delay": 3,
          "max_relogin_times": 0
        },
        "_rate_limit": {
          "enabled": false,
          "frequency": 0,
          "bucket_size": 0
        },
        "ignore_invalid_cqcode": false,
        "force_fragmented": true,
        "heartbeat_interval": 0,
        "http_config": {
          "enabled": true,
          "host": "0.0.0.0",
          "port": 5700,
          "timeout": 0,
          "post_urls": {}
        },
        "ws_config": {
          "enabled": true,
          "host": "0.0.0.0",
          "port": 6700
        },
        "ws_reverse_servers": [
          {
            "enabled": true,
            "reverse_url": "ws://127.0.0.1:8080/cqhttp/ws",
            "reverse_api_url": "",
            "reverse_event_url": "",
            "reverse_reconnect_interval": 3000
          }
        ],
        "post_message_format": "string",
        "use_sso_address": false,
        "debug": false,
        "log_level": "",
        "web_ui": {
          "enabled": true,
          "host": "0.0.0.0",
          "web_ui_port": 9999,
          "web_input": false
        }
      }
      ```

      其中 `ws://127.0.0.1:8080/cqhttp/ws` 中的 `127.0.0.1` 和 `8080` 应分别对应 nonebot 配置的 HOST 和 PORT

      

      **其中以下配置项务必按照下方样式修改！**

      ```json
      "ws_reverse_servers": [
          {
            "enabled": true,
            "reverse_url": "ws://127.0.0.1:8080/cqhttp/ws",
            "reverse_api_url": "",
            "reverse_event_url": "",
            "reverse_reconnect_interval": 3000
          }
        ],
      ```

      4. 再次运行 exe 文件或者使用 `./go-cqhttp` 启动
### 二、部署聊天插件
#### 第一次部署

1. 下载代码到本地

2. 参照 [ELF_RSS 2.0的部署方式](https://github.com/Quan666/ELF_RSS/tree/2.0) 

3. 运行 `pip install -r requirements.txt` 

4. 请按照 注释 修改配置文件 （文件 `.env.prod` ）

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

