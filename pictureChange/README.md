## 插件描述

- 支持运用百度AI进行图像处理
- 支持运用stable diffusion webui进行图像处理
- 支持运用stable diffusion webui画图
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

PS: 修改了pictureChange的`host`和`port`和`sd_model_checkpoint`和 `api_key` ,`secret_key`

### 图生图请求格式

## 个人号
-群聊 
1. 需要发送"开启图生图"之后自动识别群聊里的每一张图
2. 不需要则发送"关闭图生图"之后关闭功能
![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/bfb66026-6e43-4157-b08d-9d7b20568ef6)
![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/57096c68-2f68-4cf3-823b-88fb309664e1)

## 公众号和企业微信 
- 直接发图即可使用功能
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
1. 确保stable diffusion webui部署成功且能访问
2. 把`config.json.template`复制为`config.json`，并修改其中的参数和规则。
具体如下
```bash
# config.json文件内容示例
{
    "max_number":3, #最大并行人数量
     #申请地址https://ai.baidu.com/ai-doc
    "api_key" : "你的百度云api_key",
    "secret_key" : "你的百度云secret_key",
    "use_group": [],#不用填 
    "start": {
        "host": "你的sd画图的ip",#填上你的ip
        "port": 80,#填上你的ip的端口号
        "use_https": false
    },
     "defaults": {
        "params": {
            "sampler_name": "Euler a",
            "steps": 20,
            "width": 512,
            "height": 512,
            "cfg_scale": 7,
            "prompt": "absurdres, 8k",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "enable_hr": false,
            "hr_scale": 2,
            "hr_upscaler": "Latent",
            "hr_second_pass_steps": 15,
            "denoising_strength": 0.7
        },
        "options": {
            "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
        }
    },
    "rules": [
        {
            "keywords": [
                "横版",
                "壁纸"
            ],
            "params": {
                "width": 640,
                "height": 384
            },
            "desc": "分辨率会变成640x384"
        },
        {
            "keywords": [
                "竖版"
            ],
            "params": {
                "width": 384,
                "height": 640
            },
            "desc": "分辨率会变成384x640"
        },
        {
            "keywords": [
                "机甲少女"
            ],
            "params": {
                "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
                "prompt": "masterpiece, best quality,<lora:粉色机甲少女_v1.0:1>"
            },
            "desc": "输出机甲少女风格"
        },
        {
            "keywords": [
                "港风"
            ],
            "params": {
                "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
                "prompt": "masterpiece, best quality,<lora:gff:1>"
            },
            "desc": "输出港风风格"
        },
        {
            "keywords": [
                "国风"
            ],
            "params": {
                "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
                "prompt": "masterpiece, best quality, <lora:Domineering-and-cute-national-style-v1:1>"
            },
            "desc": "输出国风风格"
        },
        {
            "keywords": [
                "高清"
            ],
            "params": {
                "enable_hr": true,
                "hr_scale": 1.4
            },
            "desc": "出图分辨率长宽都会提高1.4倍"
        },
        {
            "keywords": [
                "二次元"
            ],
            "params": {
                "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
                "prompt": "masterpiece, best quality"
            },
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            },
            "desc": "使用二次元风格模型出图"
        },
        {
            "keywords": [
                "现实"
            ],
            "params": {
                "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
                "prompt": "masterpiece, best quality"
            },
            "options": {
                "sd_model_checkpoint": "absolutereality_v181.safetensors [463d6a9fe8]"
            },
            "desc": "使用现实风格模型出图"
        },
        {
            "keywords": [
                "Q版"
            ],
            "params": {
                "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
                "prompt": "masterpiece, best quality"
            },
            "options": {
                "sd_model_checkpoint": "QteaMix-fp16.safetensors [0c1efcbbd6]"
            },
            "desc": "使用Q版风格模型出图"
        }
    ],
    "roles": [
        {
            "title": "🌈 温柔女孩（强推）",
            "prompt": "multiple girls,masterpiece, best quality, <lora:81401-86361-lovers-avatar-v1.0:1>",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "denoising_strength": 0.4,
            "cfg_scale": 7.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "👧 可爱女生",
            "prompt": "multiple girls,Masterpiece,best quality, <lora:cozy anime_20230630155224:1>",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "denoising_strength": 0.5,
            "cfg_scale": 7.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "🧑 帅气男神",
            "prompt": "multiple boys, male focus, topless male, messy hair, looking at viewer, outdoors, beautiful lighting, deep shadow, best quality, masterpiece, ultra highres, photorealistic, blurry background,",
            "negative_prompt": "cartoon, anime, sketches,(worst quality, low quality), (deformed, distorted, disfigured), (bad eyes, wrong lips, weird mouth, bad teeth, mutated hands and fingers:1.2), bad anatomy, wrong anatomy, amputation, extra limb, missing limb, floating limbs, disconnected limbs, mutation, ugly, disgusting, (bad_pictures, negative_hand-neg:1.2)",
            "denoising_strength": 0.45,
            "cfg_scale": 8.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "💑 动漫情侣（推荐）",
            "prompt": "couple,masterpiece, best quality, <lora:81401-86361-lovers-avatar-v1.0:1>",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "denoising_strength": 0.4,
            "cfg_scale": 7.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "🦄 Q版可爱",
            "prompt": "masterpiece, best quality, <lora:81401-86361-lovers-avatar-v1.0:1>",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "denoising_strength": 0.45,
            "cfg_scale": 7.0,
            "options": {
                "sd_model_checkpoint": "QteaMix-fp16.safetensors [0c1efcbbd6]"
            }
        },
        {
            "title": "💖 Q版情侣",
            "prompt": "couple,masterpiece, best quality  <lora:81401-86361-lovers-avatar-v1.0:1>",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "denoising_strength": 0.4,
            "cfg_scale": 7.0,
            "options": {
                "sd_model_checkpoint": "QteaMix-fp16.safetensors [0c1efcbbd6]"
            }
        },
        {
            "title": "🏎 机甲女孩",
            "prompt": "multiple girls,<lora:粉色机甲少女_v1.0:1>,masterpiece, best quality,girls",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "denoising_strength": 0.5,
            "cfg_scale": 8.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "🌸 美丽女孩",
            "prompt": "multiple girls,<lora:flower:1>,masterpiece, best quality",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "denoising_strength": 0.45,
            "cfg_scale": 8.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        }
    ]
}
```
PS: 如果你下载了多个模型，就可以根据实际需要，填入你想要的模型 请确保你填入的模型是你下载过的模型，且模型能正常使用！

3. 修改文件
## 个人号
1. 直接把[chat_channel.py](https://github.com/Yanyutin753/wechat_pictureChange/blob/main/%E4%B8%AA%E4%BA%BA%E5%8F%B7/chat_channel.py)覆盖你的chatgpt-on-wechat\channel\chat_channel.py
2. 直接把[godcmd.py](https://github.com/Yanyutin753/wechat_pictureChange/blob/main/%E5%85%AC%E4%BC%97%E5%8F%B7%E5%92%8C%E4%BC%81%E4%B8%9A%E5%BE%AE%E4%BF%A1/godcmd.py)覆盖你的chatgpt-on-wechat\plugins\godcmd\godcmd.py

### 公众号和企业微信
1. 直接把[godcmd.py](https://github.com/Yanyutin753/wechat_pictureChange/blob/main/%E5%85%AC%E4%BC%97%E5%8F%B7%E5%92%8C%E4%BC%81%E4%B8%9A%E5%BE%AE%E4%BF%A1/godcmd.py)覆盖你的chatgpt-on-wechat\plugins\godcmd\godcmd.py

### 使用实例

### 贡献与支持
- 欢迎贡献代码，提出问题和建议。如果你发现了bug或者有新的功能想法，请提交一个Issue让我知道。你也可以通过Fork项目并提交Pull Request来贡献代码。 如果你喜欢这个项目，欢迎给它一个星星⭐，这是对我最大的支持！
- 敲代码不易，希望客官给点赞助，让我更好修改代码！
![91257fbc87ddb46574a4395abbb1820](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/9591e04b-7bf3-46b1-9266-7704add71fc9)


