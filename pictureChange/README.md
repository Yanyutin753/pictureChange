## 插件描述

- 可以运用百度AI进行图像处理
- 可以运用stable diffusion webui进行图像处理
- 可以运用stable diffusion webui画图
- 支持多种sd模型
- 支持并发控制
- 支持管理员修改Host
- 支持自定义模板
- 支持管理员开关群聊的图生图
- 支持管理员开关图生图功能，不影响文生图
- 支持企业微信，个人号，公众号部署

## 环境要求

使用前先安装stable diffusion webui，并在它的启动参数中添加 "--api"。

安装具体信息，请参考[视频](https://www.youtube.com/watch?v=Z6FmiaWBbAE&t=3s)。

部署运行后，保证主机能够成功访问http://127.0.0.1:7860/

如果是服务器部署则不必需要内网穿透，如果是本地电脑部署推荐[cpolar](https://dashboard.cpolar.com/signup)启动内网穿透

请确保**安装**本插件的依赖包```pip3 install -r requirements.txt```

```
pip3 install -r requirements.txt
```

## 使用说明

请将`config.json.template`复制为`config.json`，并修改其中的参数和规则。

PS: 如果修改了pictureChange的`host`和`port`，

### 图生图请求格式

## 个人号
-群聊 
1.需要发送"开启图生图"之后自动识别群聊里的每一张图
2.不需要则发送"关闭图生图"之后关闭功能
![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/bfb66026-6e43-4157-b08d-9d7b20568ef6)
![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/57096c68-2f68-4cf3-823b-88fb309664e1)

## 公众号和企业微信 
直接发图即可使用功能
![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/d6f4943c-3399-4c2d-8cb5-578aa55de509)


## godcmd添加功能
- 个人号使用一键开启或关闭图生图功能
- 更改Host(更改地址,由于本地部署内网穿透，每次的ip不同，需要更改)
![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/3a4f34d2-917d-4928-98dc-2d7e1d6dd766)


## 实现分流控制
- 当请求数超过3的时候，会发送消息，需要用户等待一会，直至前面用户完成任务之后再进行
![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/16234431-bbd9-4c5d-ad79-d545c10606e3)


### 画图请求格式

用户的画图请求格式为:

```
    <画图触发词><关键词1> <关键词2> ... <关键词n>:<prompt> 
```

例如: 画高清 现实:男孩，强壮，挺拔，running，黑色耳机，白色短袖（中间有个羊字），黑色头发，黑色短裤

会触发三个关键词 "高清", "现实",


PS: 实际参数分为两部分:

- 一部分是`params`，为画画的参数;参数名**必须**与webuiapi包中[txt2img api](https://github.com/mix1009/sdwebuiapi/blob/fb2054e149c0a4e25125c0cd7e7dca06bda839d4/webuiapi/webuiapi.py#L163)的参数名一致
- 另一部分是`sd_model_checkpoint`，它必须和你下载的模型(http://127.0.0.1:7860/sdapi/v1/options )一致。


### 部署操作
1.确保stable diffusion webui部署成功且能访问
2.把
