import base64
import os
from django.conf import settings
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def plot_rank(song_list):
    # 打開PNG圖片
    image_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'equallove_background.png')
    img = Image.open(image_path)

    # 創建可繪製對象
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('Arial Unicode.ttf', size=100)

    # 添加文字
    position = (290, 650)  # 文字的左上角位置 (x, y)
    text_color = (0, 0, 0)
    for i in song_list:
        text = i
        draw.text(position, text, font=font, fill=text_color)
        position += (0, 320)

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_image
