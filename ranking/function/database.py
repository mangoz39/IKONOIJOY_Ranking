import json

from django.db.models import Count
from collections import Counter

from ranking.models import UserChoice


def record_user_choice(session_id, ip=None, oshi=[], song_list=None):
    """

    parameter：
        session_id (str): 用戶的會話ID
        ip (str, optional)
        love (str, optional):
        me (str, optional):
        joy (str, optional):
        song (list, optional):
        img (str, optional)

    return：
        UserChoice:
    """
    try:
        # transform list to json file
        song_list_json = json.dumps(song_list) if song_list is not None else None

        # 創建並保存記錄
        user_choice = UserChoice(
            session_id=session_id,
            ip=ip,
            love=oshi[0],
            me=oshi[1],
            joy=oshi[2],
            song=song_list_json,
        )
        user_choice.save()

        return user_choice

    except Exception as e:
        print(f"記錄選擇時出錯：{e}")
        return None


def get_user_choices(session_id):
    choices = UserChoice.objects.filter(session_id=session_id).order_by('-timestamp')
    result = []

    for choice in choices:
        song_list = json.loads(choice.song_list_json) if choice.song_list_json else []

        result.append({
            'id': choice.id,
            'ip': choice.ip,
            'oshi_love': choice.oshi_love,
            'oshi_me': choice.oshi_me,
            'oshi_joy': choice.oshi_joy,
            'song_list': song_list,
            'timestamp': choice.timestamp
        })

    return result


def get_oshi_statistics():
    """
    統計各個 oshi 選項被選擇的次數

    返回:
        dict: 包含三個字典，分別對應 oshi_love, oshi_me, oshi_joy 的統計結果
    """
    result = {
        'oshi_love': {},
        'oshi_me': {},
        'oshi_joy': {},
        'song_list': {}
    }

    # 統計 oshi_love
    love_stats = UserChoice.objects.values('love').annotate(
        count=Count('id')
    ).order_by('-count')

    for item in love_stats:
        if item['love']:  # 跳過空值
            result['oshi_love'][item['love']] = item['count']

    # 統計 oshi_me
    me_stats = UserChoice.objects.values('me').annotate(
        count=Count('id')
    ).order_by('-count')

    for item in me_stats:
        if item['me']:  # 跳過空值
            result['oshi_me'][item['me']] = item['count']

    # 統計 oshi_joy
    joy_stats = UserChoice.objects.values('joy').annotate(
        count=Count('id')
    ).order_by('-count')

    for item in joy_stats:
        if item['joy']:  # 跳過空值
            result['oshi_joy'][item['joy']] = item['count']

    song_counter = Counter()
    all_choices = UserChoice.objects.all()

    for choice in all_choices:
        if choice.song:
            try:
                songs = json.loads(choice.song)
                if isinstance(songs, list):
                    song_counter.update(songs)
            except json.JSONDecodeError:
                # 處理可能的JSON解析錯誤
                continue

        # 將計數結果轉換為字典
    result['song_list'] = dict(song_counter.most_common())

    return result


