# ELFChatBot

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1b642ec8ccd240bebc63cd37d7337e3d)](https://app.codacy.com/gh/Quan666/ELFChatBot?utm_source=github.com&utm_medium=referral&utm_content=Quan666/ELFChatBot&utm_campaign=Badge_Grade_Settings)

> **这是一个闲聊机器人，基于 [Nonebot2](https://v2.nonebot.dev/guide/)**  
> **接入了腾讯和百度的闲聊 api，百度的api支持连续对话**  
> **可以实现群聊、私聊，同时随机回复群聊消息。**  
> **支持 ChatGPT（感谢 https://github.com/acheong08/ChatGPT 项目）**  

效果图：

![image-20210114125523902](https://cdn.jsdelivr.net/gh/Quan666/CDN/pic/image-20210114125523902.png)

## 使用

私聊或群里 @bot 即可触发聊天，结束回复设定的关键词即可

ChatGPT： 发送 `chatgpt` 命令触发

## 娱乐功能
  1. 随机回复群友消息
  2. 伪造转发合并消息（fake、fakes触发，具体使用看代码）

## 申请密钥

1. 百度大脑平台（推荐使用！）

   https://ai.baidu.com/unit/home 注册并创建机器人，设置好机器人技能（至少包含闲聊），得到机器人id（S开头）、`api_key`、`secret_key`

   注意：默认优先使用百度
   
   
2. ~~腾讯开放平台（推荐作为备用也申请一个）~~ 失效了

   ~~前往 [https://ai.qq.com/console/capability/detail/8](https://ai.qq.com/console/capability/detail/8) 注册并创建应用，并在能力库接入 智能闲聊，得到 `app_id` 以及 `app_key`~~


3. 注册 openai 
   
   OpenAI: [https://chat.openai.com/chat](https://chat.openai.com/chat)

   在cookie中找到 __Secure-next-auth.session-token 通过 `chatgpt_token` 命令设置
   
   国内服务器需要以下步骤二选一：

    1. 使用 cloudflare 反代 chat.openai.com ，将 `chatgpt_cf_proxy.js` 文件内代码复制部署到 cloudflare workers 并配置自定义域名，将域名填入如 `chatgpt_host=https://chatgpt.iy.ci`

    2. 配置代理(e: chat_proxy="127.0.0.1:7890")

   使用： 
    发送 `chatgpt 问题` 即可，在群组需要在前面 @机器人


## 部署

**注意：Python 3.8+**


1. 下载代码到本地

2. 参照 [ELF_RSS 2.0的部署方式](https://github.com/Quan666/ELF_RSS/tree/2.0) 

3. 运行 `pip install -r requirements.txt` 

4. 请按照 注释 修改配置文件 （文件 `.env.prod` ）

5. 运行 `nb run`

6. 收到机器人发送的启动成功消息


#### 已经部署过其它 Nonebot2 机器人

1. 下载 项目文件夹 `src/plugins/ELFChatBot` 复制 到你部署好了的机器人 `plugins` 目录
2. 下载 `requirements.txt` 文件，并运行 `pip install -r requirements.txt` 
3. 同 `第一次部署` 一样，修改配置文件
4. 运行 `nb run`

