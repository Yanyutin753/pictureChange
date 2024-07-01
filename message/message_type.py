# 接收到图片消息时的回复格式
def in_image_reply(file_content, request_bot_name, role_options, use_stable_diffusion,
                   use_music_handle, use_file_handle, is_wecom):
    if not is_wecom:
        replyText = (f"\n🥰 您的图片编号:\n💖 {file_content}\n\n❗ 请输入指令,以进行图片操作\n"
                     f"✅ 支持以下指令")
        if use_music_handle:
            replyText += f"\n\n{request_bot_name}🎧 图生音 {file_content}"

        if use_file_handle:
            replyText += f"\n\n{request_bot_name}🖼️ 图像描述  {file_content}"

        if use_stable_diffusion:
            replyText += f"\n\n{request_bot_name}🤖 图像修复 {file_content}"

            for role in role_options:
                replyText += f"\n\n{request_bot_name} {role['title']} {file_content}"

            replyText += f"\n\n{request_bot_name}🎡 自定义 {file_content} [关键词] 例如 黑色头发 白色短袖 等关键词"

        replyText += f"\n\n{request_bot_name}⭐ 暂不处理 {file_content}"

    else:
        replyText = f"🥰 您的图片编号:\n💖 {file_content}\n\n❗ 请点击指令,以进行图片操作"
        if use_music_handle:
            replyText += ("\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={}{} {}\">{}</a>".
                          format(request_bot_name, "🎧 图生音", file_content, "🎧 图生音"))
        if use_file_handle:
            replyText += ("\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={}{} {}\">{}</a>".
                          format(request_bot_name, "🖼️ 图像描述", file_content, "🖼️ 图像描述"))

        if use_stable_diffusion:
            replyText += ("\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={}{} {}\">{}</a>".
                          format(request_bot_name, "🤖 图像修复", file_content, "🤖 图像修复"))
            for role in role_options:
                replyText += ("\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={}{} {}\">{}</a>".
                              format(request_bot_name, role['title'], file_content, role['title']))
            replyText += f"\n\n{request_bot_name}🎡 自定义 {file_content} [关键词] 例如 黑色头发 白色短袖 等关键词"

        replyText += ("\n\n<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={}{} {}\">{}</a>".
                      format(request_bot_name, "⭐ 暂不处理", file_content, "⭐ 暂不处理"))

    if use_stable_diffusion:
        replyText += "\n\n🥰 温馨提示\n👑 MODEL_1 : 动漫\n🏆 MODEL_2 : 现实\n🧩 MODEL_3 : Q版"

    replyText += "\n\n🚀 发送指令后，请耐心等待一至两分钟，作品将很快呈现出来！"
    return replyText


# 图片消息时的回复格式
def on_image_reply(request_bot_name, image_type, all_seeds, modelname, minutes, seconds, is_wecom):
    replyText = f"🔥 图片创作成功!\n⏱ 图片处理耗时：{minutes}分钟 {seconds}秒\n🧸点击指令，我将为您进行图片操作！\n\n✅ 支持指令"
    composition_1 = 0
    composition_2 = 0
    if not is_wecom:
        for seed in all_seeds:
            composition_1 += 1
            replyText += ("\n\n{} 🤖 放大 {}.png {}"
                          .format(request_bot_name, f"{image_type}/{seed}", composition_1))
        for seed in all_seeds:
            composition_2 += 1
            replyText += ("\n\n{} 🎡 变换 {}.png {} {}"
                          .format(request_bot_name, f"{image_type}/{seed}", modelname, composition_2))
    else:
        for seed in all_seeds:
            composition_1 += 1
            if composition_1 % 2 == 0:
                replyText += "\t\t"
            else:
                replyText += "\n\n"
            replyText += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={}🔍 放大 {}.png\">{}</a>".format(
                request_bot_name, f"txt2img-images/{seed}", f"🤖 放大 {composition_1}")
        for seed in all_seeds:
            composition_2 += 1
            if composition_2 % 2 == 0:
                replyText += "\t\t"
            else:
                replyText += "\n\n"
            replyText += "<a href=\"weixin://bizmsgmenu?msgmenuid=1&msgmenucontent={}🎡 变换 {}.png {}\">{}</a>".format(
                request_bot_name, f"txt2img-images/{seed}", modelname, f"🎡 变换 {composition_2}")
    replyText += ("\n\n🥰 温馨提示\n✨ 1:左上 2:右上 3:左下 4:右下\n👑 MODEL_1 : 动漫\n🏆 MODEL_2 : 现实\n🧩 MODEL_3 : Q版\n🌈 "
                  f"图片不满意的话，点击变换\n{request_bot_name}帮你再画一幅吧!\n💖 感谢您的使用！")
    return replyText


# 用于主函数的帮助回复
def on_help_reply(trigger, rules):
    help_text = "💨利用百度云和stable-diffusion webui来画图,图生图\n"
    help_text += (
        f"💖使用方法:\n\"{trigger}[关键词1] [关键词2]...:提示语\"的格式作画，如\"{trigger}画高清:男孩，强壮，挺拔，running"
        f"，黑色耳机，白色短袖（中间有个羊字），黑色头发，黑色短裤\"\n")
    help_text += "🥰目前可用关键词：\n"
    for rule in rules:
        keywords = [f"[{keyword}]" for keyword in rule['keywords']]
        help_text += f"{','.join(keywords)}"
        if "desc" in rule:
            help_text += f"-{rule['desc']}\n"
        else:
            help_text += "\n"
    help_text += (
        "🥰发送 '一张图片'，我将为您进行图片操作\n"
    )
    return help_text
