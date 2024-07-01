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

### 1.使用前先安装stable diffusion webui，并在它的启动参数中添加 "--api",并开启**种子数**。

* 安装具体信息，请参考[视频](https://www.youtube.com/watch?v=Z6FmiaWBbAE&t=3s)。
* 部署运行后，保证主机能够成功访问http://127.0.0.1:7860/
* 如果是服务器部署则不必需要内网穿透，如果是本地电脑部署推荐[cpolar](https://dashboard.cpolar.com/signup)启动内网穿透

#### **如下图**

![image](https://github.com/Yanyutin753/pictureChange/assets/132346501/7c58fde5-832c-4e8d-b822-0117cd77814f)

#### **请确保图片的文件名字有种子数进行命名**

![image](https://github.com/Yanyutin753/pictureChange/assets/132346501/5e310369-011d-430c-a85b-ca95946af799)

### 2.如果你的**chatgpt-on-wechat

**是最新版，[请点击查看](https://github.com/Yanyutin753/pictureChange/issues/9#issuecomment-2024305057)

### 3.**确保图片位置填写正确**

![image](https://github.com/Yanyutin753/pictureChange/assets/132346501/7736b31e-c58c-47b0-8f44-0dc167d43027)

```
"file_url": "file=D:/sd/sd-webui-aki/sd-webui-aki-v4.2/sd-webui-aki-v4.2/outputs,  #这个地址是你图片生成的地址"
```

### 4.请确保**安装**本插件的依赖包```pip3 install -r requireents.txt```

```
pip3 install -r requirements.txt
```

## 使用说明

请将`config.json.template`复制为`config.json`，并修改其中的参数和规则。

PS: 修改了pictureChange的`host`和`port`和`sd_model_checkpoint`和 `api_key` ,`secret_key`，并填充相应的模型名称

### 图生图请求格式

## 个人号

- 群聊

1. 需要发送"开启图生图"之后自动识别群聊里的每一张图
2. 不需要则发送"关闭图生图"之后关闭功能
   ![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/1813d361-242f-4ac1-8cbf-c0282e95f34e)

- 单聊
  直接发照片即可

## 公众号和企业微信

- 直接发图即可使用功能
  ![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/6a3559ff-f538-469d-84b8-4446bf814207)

## godcmd添加功能

- 个人号使用一键开启或关闭图生图功能
- 更改Host(更改地址,由于本地部署内网穿透，每次的ip不同，需要更改)
  ![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/722ad22c-ef26-47e0-a105-86b8ffc02a08)

## 实现分流控制

- 当请求数超过3的时候，会发送消息，需要用户等待一会，直至前面用户完成任务之后再进行
  ![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/8f56227b-e8b2-49a1-902b-1812f8336765)

### 画图请求格式

用户的画图请求格式为:

```
    <画图触发词><关键词1> <关键词2> ... <关键词n>:<prompt> 
```

例如: 画高清 现实:男孩，强壮，挺拔，running，黑色耳机，白色短袖（中间有个羊字），黑色头发，黑色短裤

会触发三个关键词 "高清", "现实",

PS: 实际参数分为两部分:

- 一部分是`params`，为画画的参数;参数名**必须**
  与webuiapi包中[txt2img api](https://github.com/mix1009/sdwebuiapi/blob/fb2054e149c0a4e25125c0cd7e7dca06bda839d4/webuiapi/webuiapi.py#L163)
  的参数名一致
- 另一部分是`sd_model_checkpoint`，它必须和你下载的模型(http://127.0.0.1:7860/sdapi/v1/options )一致。

### 部署操作

1. 确保stable diffusion webui部署成功且能访问
2. 安装包解压，并确保只把pictureChange文件夹plugins目录里面，之后把`config.json.template`复制为`config.json`，并修改其中的参数和规则。
   具体如下

```bash
# config.json文件内容示例
{
    "max_number":3, #最大并行人数量
    "request_bot_name" : "群聊请求机器人的名称，和config.json环境变量一致（只限一个）",
    "file_url": "file=D:/sd/sd-webui-aki/sd-webui-aki-v4.2/sd-webui-aki-v4.2/outputs,  #这个地址是你图片生成的地址"
    "is_use_fanyi":false, #是否使用翻译，true就直接使用百度翻译，false使用gpt优化提示词
     #申请地址https://ai.baidu.com/ai-doc
    "api_key" : "你的百度云api_key",
    "secret_key" : "你的百度云secret_key",
    "use_group": [],#不用填
    "max_size": 1150,
    "start": {
        "host": "你的sd画图的ip",#填上你的ip
        "port": 80,#填上你的ip的端口号
        "use_https": false
    },
      "defaults": {
        "params": {
            "sampler_name": "DPM++ 2M Karras",
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
            }
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
            "title": "🌈 图像动漫化",
            "prompt": "masterpiece, best quality",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "denoising_strength": 0.45,
            "cfg_scale": 7.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "👧 可爱女生",
            "prompt": "masterpiece, best quality",
            "negative_prompt": "paintings, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, glans, extra fingers, fewer fingers, ((watermark:2)), (white letters:1), (multi nipples), bad anatomy, bad hands, text, error, missing fingers, missing arms, missing legs, extra digit, fewer digits, cropped, worst quality, jpeg artifacts, signature, watermark, username, bad feet, Multiple people, blurry, poorly drawn hands, poorly drawn face, mutation, deformed, extra limbs, extra arms, extra legs, malformed limbs, fused fingers, too many fingers, long neck, cross-eyed, mutated hands, polar lowres, bad body, bad proportions, gross proportions, wrong feet bottom render, abdominal stretch, briefs, knickers, kecks, thong, fused fingers, bad body,bad proportion body to legs, wrong toes, extra toes, missing toes, weird toes, 2 body, 2 pussy, 2 upper, 2 lower, 2 head, 3 hand, 3 feet, extra long leg, super long leg, mirrored image, mirrored noise,, badhandv4, ng_deepnegative_v1_75t",
            "denoising_strength": 0.45,
            "cfg_scale": 8.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "🧑 帅气男神",
            "prompt": "boy, male focus, topless male, messy hair, looking at viewer, outdoors, beautiful lighting, deep shadow, best quality, masterpiece, ultra highres, photorealistic, blurry background,",
            "negative_prompt": "cartoon, anime, sketches,(worst quality, low quality), (deformed, distorted, disfigured), (bad eyes, wrong lips, weird mouth, bad teeth, mutated hands and fingers:1.2), bad anatomy, wrong anatomy, amputation, extra limb, missing limb, floating limbs, disconnected limbs, mutation, ugly, disgusting, (bad_pictures, negative_hand-neg:1.2)",
            "denoising_strength": 0.45,
            "cfg_scale": 8.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "💑 二次元情侣",
            "prompt": "absurdres, highres, ultra detailed, (:1.3), BREAK , Create a vintage advertisement, with retro design elements, classic typography, and a nostalgic atmosphere. BREAK , Create an image of a half-human, half-dragon hybrid, with a combination of physical features and powers from both of their parentage. BREAK , Create an image with a shallow depth of field, focusing on the subject and blurring the background for a sense of depth and separation. BREAK , Illustrate an old-town street, with historic buildings, cobblestone streets, and a sense of charm and nostalgia. BREAK , Capture a tender moment between a couple, showcasing their love, intimacy, and emotional connection. BREAK , Illustrate an image using soft pastel colors, with a gentle, dreamy quality and a focus on light and atmosphere.",
            "negative_prompt": "EasyNegative, (worst quality, low quality:1.4), nsfw, (blush:1.3), logo",
            "denoising_strength": 0.45,
            "cfg_scale": 8.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "🦄 Q版化图像",
            "prompt": "masterpiece, best quality",
            "negative_prompt": "(((nsfw))),EasyNegative,badhandv4,ng_deepnegative_v1_75t,(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), bad anatomy,DeepNegative, skin spots, acnes, skin blemishes,(fat:1.2),facing away, looking away,tilted head, lowres,bad anatomy,bad hands, missing fingers,extra digit, fewer digits,bad feet,poorly drawn hands,poorly drawn face,mutation,deformed,extra fingers,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands,polar lowres,bad body,bad proportions,gross proportions,missing arms,missing legs,extra digit, extra arms, extra leg, extra foot,teethcroppe,signature, watermark, username,blurry,cropped,jpeg artifacts,text,error,Lower body exposure",
            "denoising_strength": 0.7,
            "cfg_scale": 7.0,
            "options": {
                "sd_model_checkpoint": "QteaMix-fp16.safetensors [0c1efcbbd6]"
            }
        },
        {
            "title": "🏎 机甲女孩",
            "prompt": "absurdres, highres, ultra detailed, (1girl:1.3), BREAK , Sun Knight, solar magic, light manipulation, radiant power, sunbeam attacks, aura of warmth, shining armor BREAK , photo manipulation, altered realities, fantastical scenes, digital artistry, creative editing, evocative narratives, striking visuals BREAK , kinetic art, moving sculptures, mechanical creations, interactive installations, dynamic motion, engineering ingenuity, captivating visuals",
            "negative_prompt": "EasyNegative, (worst quality, low quality:1.4), nsfw",
            "denoising_strength": 0.45,
            "cfg_scale": 7.0,
            "options": {
                "sd_model_checkpoint": "anything-v5-PrtRE.safetensors [7f96a1a9ca]"
            }
        },
        {
            "title": "🌸 樱花女孩",
            "prompt": "(masterpiece, high quality, highres,illustration),blurry background,[(white background:1.2)::5],cowboy shot, spring (season),(no light:1.1),(temptation:1.2),elegance, (1loli:1.1),(very long hair:1.1),(blush:0.7),floating hair,ahoge,deep sky,star (sky), (summer (Floral:1.2) dress:1.1),outline,(see-through:0.85),shining,low twintails, (polychromatic peony:1.15),Movie poster,(colorful:1.1),ornament,petals,(pantyhose:1.1), ribbon",
            "negative_prompt": "sketch, duplicate, ugly, huge eyes, text, logo, worst face, (bad and mutated hands:1.3), (worst quality:2.0), (low quality:2.0), (blurry:2.0), horror, geometry, bad_prompt, (bad hands), (missing fingers), multiple limbs, bad anatomy, (interlocked fingers:1.2), Ugly Fingers, (extra digit and hands and fingers and legs and arms:1.4), ((2girl)), (deformed fingers:1.2), (long fingers:1.2),(bad-artist-anime), bad-artist, bad hand, extra legs, nipples,nsfw, Size: 384x832, Seed: 969039108, Model: MAADBD2fp16, Steps: 20, (blurry: 2.0), horror, geometry, bad_prompt, (bad hands), (missing fingers), multiple limbs, bad anatomy, Version: v1.3.2, Sampler: DPM++ 2M Karras, CFG scale: 8, Clip skip: 2, Model hash: cca17b08da, Hires steps: 20, (low quality: 2.0), (long fingers: 1.2),(bad-artist-anime), bad-artist, bad hand, extra legs, nipples,nsfw, Hires upscale: 2, (worst quality: 2.0), Hires upscaler: Latent, (deformed fingers: 1.2), Denoising strength: 0.5, (interlocked fingers: 1.2), Ugly Fingers, (bad and mutated hands: 1.3), Wildcard negative prompt: sketch, duplicate, ugly, huge eyes, text, logo, worst face, (extra digit and hands and fingers and legs and arms: 1.4), ((2girl))",
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

1.

直接把[godcmd.py](https://github.com/Yanyutin753/wechat_pictureChange/blob/main/%E5%85%AC%E4%BC%97%E5%8F%B7%E5%92%8C%E4%BC%81%E4%B8%9A%E5%BE%AE%E4%BF%A1/godcmd.py)
覆盖你的chatgpt-on-wechat\plugins\godcmd\godcmd.py

2. 在根目录config.json和config.py分别添加下面代码

- config.json

```
    "group_imageChange": true,默认为True
```

- config.py

```
    "group_imageChange": False,默认为True
```

3.群聊的时候记得先发送@机器人 开启图生图，才能正常使用功能

### 公众号和企业微信

1.

直接把[godcmd.py](https://github.com/Yanyutin753/wechat_pictureChange/blob/main/%E5%85%AC%E4%BC%97%E5%8F%B7%E5%92%8C%E4%BC%81%E4%B8%9A%E5%BE%AE%E4%BF%A1/godcmd.py)
覆盖你的chatgpt-on-wechat\plugins\godcmd\godcmd.py

4. 安装依赖

```
    #进入pictureChange文件夹安装依赖
    pip3 install -r requirements.txt
```

### 使用实例

- 图生图

![image](https://github.com/Yanyutin753/pictureChange/assets/132346501/4d6f16b0-136a-48d6-991e-482ce3bbc701)

![image](https://github.com/Yanyutin753/pictureChange/assets/132346501/783d6f22-c18e-4368-bc91-aa62a24c0c78)

![9d3c926daec3b69ef1f2e1b38e4ad7e](https://github.com/Yanyutin753/pictureChange/assets/132346501/cc5f8843-6a42-422c-bbeb-1c073ffa651b)

- 画图

![image](https://github.com/Yanyutin753/pictureChange/assets/132346501/428a2333-1589-42fd-88df-a1b182f8b3f6)

![image](https://github.com/Yanyutin753/pictureChange/assets/132346501/89782b7c-8f28-42af-8c16-a588539219a3)

- 支持放大 变换操作

![image](https://github.com/Yanyutin753/pictureChange/assets/132346501/1ab662b2-bd3c-490f-9981-404dcb1ca0e3)

![image](https://github.com/Yanyutin753/pictureChange/assets/132346501/32949ac2-93fc-4b7c-8387-f5cd7b1cb139)

### 贡献与支持

- 欢迎贡献代码，提出问题和建议。如果你发现了bug或者有新的功能想法，请提交一个Issue让我知道。你也可以通过Fork项目并提交Pull
  Request来贡献代码。 如果你想部署这个项目，给我一个星星⭐，这是对我最大的支持！
- 敲代码不易，希望客官给点赞助，让我更好修改代码！
  ![image](https://github.com/Yanyutin753/wechat_pictureChange/assets/132346501/713eb69e-6e00-46ad-bec5-0b3926305ef0)



