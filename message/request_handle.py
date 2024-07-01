# 识别图片消息的请求体
def recognize_message(prompt: str, image_url: str, model: str):
    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "stream": False,
        "model": model
    }


# 创造图片的请求体
def image_message(prompt: str, model: str):
    return {
        "model": model,
        "prompt": prompt
    }


# 创造音乐的请求体
def music_message(prompt: str, model: str):
    return {
        "model": model,
        "stream": False,
        "messages": [
            {
                "content": prompt,
                "role": "user"
            }
        ]
    }
