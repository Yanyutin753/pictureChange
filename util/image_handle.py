# 用于处理图片大小的工具函数
def adjust_image(width, height, maxsize: int):
    # 确保最小尺寸为 768
    if width < 768 or height < 768:
        scale_factor = max(768 / width, 768 / height)
        width = int(width * scale_factor)
        height = int(height * scale_factor)

    # 确保最大尺寸不超过 maxsize
    if width > maxsize or height > maxsize:
        scale_factor = min(maxsize / width, maxsize / height)
        width = int(width * scale_factor)
        height = int(height * scale_factor)

    return int(width), int(height)


# 用于格式化图片 URL 的工具函数
def format_image_url(use_https, host, port, file_url, file_content):
    protocol = "https" if use_https else "http"
    port_part = f":{port}" if port else ""
    image_path = f"{file_url}{file_content}"
    image_url = f"{protocol}://{host}{port_part}/{image_path}"
    return image_url
