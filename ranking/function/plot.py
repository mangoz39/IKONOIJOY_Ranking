import base64
import os
from django.conf import settings
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def group_info_process(song_count, oshi):
    match song_count:
        case 15:
            return 2, "nearly_equal_joy_back.png", oshi[2]
        case 49:
            if oshi[1] == "川中子奈月心" or "菅波美玲":
                return 1, "not_equal_me_back_1.png", oshi[1]
            elif oshi[1] == "蟹沢萌子" or "冨田菜々風":
                return 1, "not_equal_me_back_2.png", oshi[1]
            elif oshi[1] == "永田詩央里" or "本田珠由記":
                return 1, "not_equal_me_back_3.png", oshi[1]
            elif oshi[1] == "尾木波菜" or "櫻井もも":
                return 1, "not_equal_me_back_4.png", oshi[1]
            elif oshi[1] == "鈴木瞳美" or "谷崎早耶":
                return 1, "not_equal_me_back_5.png", oshi[1]
            elif oshi[1] == "河口夏音" or "落合希来里":
                return 1, "not_equal_me_back_6.png", oshi[1]
            else:
                return 1, "not_equal_me_back_2.png", oshi[1]
        case 72:
            return 0, "equal_love_back.png", oshi[0]
        case _:
            return 3, "ikonoijoy_back.png", f'\n{oshi[0]}\n{oshi[1]}\n{oshi[2]}'


def get_text_position(text, center_x, center_y, font):

    bbox = font.getmask(text).getbbox()
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 計算 draw.text() 需要的左上角座標
    x_position = center_x - (text_width // 2)
    y_position = center_y - (text_height // 2)

    return x_position, y_position


def plot_rank(song_list, count, oshi):
    # 紀錄預設位置
    love_position_x = 776
    love_position_y = 740
    love_footer = 110, 3800
    me_position_x = 776
    me_position_y = 580
    me_footer = 110, 4284
    joy_position_x = 776
    joy_position_y = 580
    joy_footer = 110, 4254

    group_info, img_info, oshi_name = group_info_process(count, oshi)
    image_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', img_info)
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('Arial Unicode.ttf', size=100)

    match group_info:
        case 0:
            position_x, position_y, position_f, footer = love_position_x, love_position_y, love_footer, f'生徒会長：{oshi_name}'
        case 1:
            position_x, position_y, position_f, footer = me_position_x, me_position_y, me_footer, f'当番：{oshi_name}'
        case 2:
            position_x, position_y, position_f, footer = joy_position_x, joy_position_y, joy_footer, f'委員長：{oshi_name}'
        case _:
            position_x, position_y, position_f, footer = love_position_x, love_position_y, love_footer, f'代表：{oshi_name}'

    for i in song_list:
        text = i
        draw.text(get_text_position(i, position_x, position_y, font), text, font=font, fill=(0, 0, 0))
        position_y += 320

    font = ImageFont.truetype('Arial Unicode.ttf', size=70)
    draw.text(position_f, footer, font=font, fill=(0, 0, 0, 200))
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_image
