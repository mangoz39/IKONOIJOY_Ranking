import json
import random
import logging

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from .function import ranking, plot, database
from .files import songs as sg

logger = logging.getLogger(__name__)


@never_cache
def index(request):
    request.session['access'] = 0
    return render(request, "index.html")


def start_ranking(request):
    """
    song_list definition:
    0: equal_love
    1: not_equal_me
    2: nearly_equal_joy
    3: ikonoijoy
    4: ikonoi
    5: ikojoy
    6: noijoy
    """

    request.session.flush()
    request.session['access'] = 1
    rand_list = []
    if request.method == 'POST':
        list_ref = request.POST.get('list_ref', '')
        oshi1 = request.POST.get('oshi1', '')
        oshi2 = request.POST.get('oshi2', '')
        oshi3 = request.POST.get('oshi3', '')
        request.session['oshi'] = [oshi1, oshi2, oshi3]

        match list_ref:
            case '1':
                song_list = 0
                song_count = sg.equal_total
            case '10':
                song_list = 1
                song_count = sg.not_equal_me_total
            case '11':
                song_list = 4
                song_count = sg.ikonoi_total
            case '100':
                song_list = 2
                song_count = sg.nearly_equal_joy_total
            case '101':
                song_list = 5
                song_count = sg.ikojoy_total
            case '110':
                song_list = 6
                song_count = sg.noijoy_total
            case '111':
                song_list = 3
                song_count = sg.ikonoijoy_total
            case _:
                return redirect('/')

        for i in range(song_count):
            rand_list.append(i)

        random.shuffle(rand_list)
        request.session["songs"] = rand_list
        request.session['song_list'] = song_list
        request.session['song_count'] = song_count

        ranker = ranking.SongRanker(rand_list)  # 建立 ranking 物件
        request.session["ranker"] = ranker.to_dict()  # 存入 session
        request.session["sorted_songs"] = []

        request.session['access'] = '1'
        return redirect('rank')

    return redirect('/')


def rank(request):
    if request.session.get("access") == '1':
        song_list = sg.slist[request.session.get('song_list')]
        ranker_data = request.session.get("ranker")
        if ranker_data is None:
            logger.warning("Invalid JSON format from client: %s")
            return redirect('/')
            # return JsonResponse({"error": "400 Bad Request (Access Denied)"}, status=400)

        # 使用 from_dict 重新建立 SongRanker 物件
        songs = request.session.get("songs", [])
        ranker = ranking.SongRanker.from_dict(ranker_data, songs)
        song_left, song_right = ranker.get_current_pair()
        if song_left == 0 and song_right == 0:
            return redirect('/')
            # return JsonResponse({"error": "400 Bad Request (Access Denied)"}, status=400)

        request.session["ranker"] = ranker.to_dict()

        return render(request, "ranking.html", {
            "finished": False,
            "song1": song_list[song_left].getName(),
            "song2": song_list[song_right].getName(),
            "song1_youtube_id": song_list[song_left].getID(),
            "song2_youtube_id": song_list[song_right].getID(),
            "song1_color": song_list[song_left].getGroup(),
            "song2_color": song_list[song_right].getGroup()
        })
    else:
        return redirect('/')
        # return JsonResponse({"error": "400 Bad Request (Access Denied)"}, status=400)


def choose_song(request):
    song_list = sg.slist[request.session.get('song_list')]
    if request.method == "POST":
        ranker_data = request.session.get("ranker")
        if ranker_data is None:
            return redirect('/')
            # return JsonResponse({"error": "400 Bad Request (Access Denied)"}, status=400)

        # 使用 from_dict 重新建立 SongRanker 物件
        songs = request.session.get("songs", [])
        ranker = ranking.SongRanker.from_dict(ranker_data, songs)

        data = json.loads(request.body)
        choice = data.get("choice")
        is_finished = ranker.choose(choice)

        request.session["ranker"] = ranker.to_dict()

        if is_finished:
            tmp_res = ranker.temp_list[0]
            tmp_ses = []
            tmp_full_list = []
            result_list = []
            if request.session.get('song_count') > 55:
                k = 10
            else:
                k = 12
            for s in tmp_res:
                result_list.append(song_list[s])

            for songs in result_list[:k]:
                tmp_ses.append(songs.getName())
            request.session["sorted_songs"] = tmp_ses

            for songs in result_list:
                tmp_full_list.append(songs.getName())
            request.session["full_sorted_songs"] = tmp_full_list

            return JsonResponse({"finished": True})

        song_left, song_right = ranker.get_current_pair()
        if song_left == 0 and song_right == 0:
            return JsonResponse({"error": "400 Bad Request (Access Denied)"}, status=400)

        return JsonResponse({
            "finished": False,
            "song1": song_list[song_left].getName(),
            "song2": song_list[song_right].getName(),
            "song1_youtube_id": song_list[song_left].getID(),
            "song2_youtube_id": song_list[song_right].getID(),
            "song1_color": song_list[song_left].getGroup(),
            "song2_color": song_list[song_right].getGroup()
        })

    return JsonResponse({"finished": True})


def result(request):
    plot_pend, song_count, oshi_list = (
        request.session.get('sorted_songs', []),
        request.session.get('song_count', 0),
        request.session.get('oshi', []))
    if plot_pend is None or song_count is None or oshi_list is None:
        return redirect('/')
        # return JsonResponse({"error": "400 Bad Request (Access Denied)"}, status=400)
    img = plot.plot_rank(plot_pend, song_count, oshi_list)
    user_id = request.session.session_key
    ip = request.META.get('REMOTE_ADDR')
    database.record_user_choice(user_id, ip, oshi_list, plot_pend)
    request.session['access'] = 0
    request.session['record'] = 1
    return render(request, "result.html", {
        'base64_image': img,
        'image_type': 'image/png'})


def record(request):
    if request.session.get('record') == 1:
        plot_pend, song_count, oshi_list = (
            request.session.get('sorted_songs', []),
            request.session.get('song_count', 0),
            request.session.get('oshi', []))
        if plot_pend is None or song_count is None or oshi_list is None:
            return render(request, "index.html")
        img = plot.plot_rank(plot_pend, song_count, oshi_list)
        return render(request, "result.html", {
            'base64_image': img,
            'image_type': 'image/png'})
    else:
        return redirect('/')


def oshi_statistics_view(request):
    stats = database.get_oshi_statistics()

    # 處理格式顯示
    formatted_stats = {
        'oshi_love': [],
        'oshi_me': [],
        'oshi_joy': [],
        'song_list': []
    }

    for name, count in stats['oshi_love'].items():
        try:
            if isinstance(name, str) and (name.startswith('{') or name.startswith('[')):
                parsed_name = json.loads(name)
                if isinstance(parsed_name, str):
                    display_name = parsed_name
                elif isinstance(parsed_name, (list, dict)):
                    display_name = str(parsed_name)
                else:
                    display_name = name
            else:
                display_name = name
        except:
            display_name = name

        formatted_stats['oshi_love'].append({
            'name': display_name,
            'count': count
        })

    for name, count in stats['oshi_me'].items():
        # 轉換JSON格式
        try:
            if isinstance(name, str) and (name.startswith('{') or name.startswith('[')):
                parsed_name = json.loads(name)
                if isinstance(parsed_name, str):
                    display_name = parsed_name
                elif isinstance(parsed_name, (list, dict)):
                    display_name = str(parsed_name)
                else:
                    display_name = name
            else:
                display_name = name
        except:
            display_name = name

        formatted_stats['oshi_me'].append({
            'name': display_name,
            'count': count
        })

    for name, count in stats['oshi_joy'].items():
        # 轉換JSON格式
        try:
            if isinstance(name, str) and (name.startswith('{') or name.startswith('[')):
                parsed_name = json.loads(name)
                if isinstance(parsed_name, str):
                    display_name = parsed_name
                elif isinstance(parsed_name, (list, dict)):
                    display_name = str(parsed_name)
                else:
                    display_name = name
            else:
                display_name = name
        except:
            display_name = name

        formatted_stats['oshi_joy'].append({
            'name': display_name,
            'count': count
        })

    # 處理 song_list
    for name, count in stats['song_list'].items():
        formatted_stats['song_list'].append({
            'name': name,
            'count': count
        })

    formatted_stats['oshi_love'] = sorted(formatted_stats['oshi_love'], key=lambda x: x['count'], reverse=True)
    formatted_stats['oshi_me'] = sorted(formatted_stats['oshi_me'], key=lambda x: x['count'], reverse=True)
    formatted_stats['oshi_joy'] = sorted(formatted_stats['oshi_joy'], key=lambda x: x['count'], reverse=True)
    formatted_stats['song_list'] = sorted(formatted_stats['song_list'], key=lambda x: x['count'], reverse=True)

    return JsonResponse({
        'success': True,
        'statistics': formatted_stats
    }, json_dumps_params={'ensure_ascii': False})


def make_bookmark(request):
    request.session.flush()
    if request.method == 'POST':
        try:
            oshi1 = request.POST.get('oshi1', '')
            oshi2 = request.POST.get('oshi2', '')
            oshi3 = request.POST.get('oshi3', '')
            request.session['oshi'] = [oshi1, oshi2, oshi3]
            background = request.POST.get('background', '0')
            match background:
                case '100':
                    request.session['song_count'] = 15
                    ref_list = sg.nearlyequaljoy_song
                    total_sel = 12
                case '10':
                    request.session['song_count'] = 51
                    ref_list = sg.notequalme_song
                    total_sel = 12
                case '1':
                    request.session['song_count'] = 72
                    ref_list = sg.equallove_song
                    total_sel = 10
                case _:
                    request.session['song_count'] = 73
                    ref_list = sg.ikonoijoy_song
                    total_sel = 10

            request.session['total_selections'] = total_sel
            song_list = []
            for s in ref_list:
                song_list.append({"name": s.getName(), "youtube_id": s.getID()})
            song_json = json.dumps(song_list)
            # print("傳遞的歌曲JSON:", song_json)

            request.session['oshi'] = [oshi1, oshi2, oshi3]
            return render(request, "bookmark.html", {
                "song_json": song_json,
                "current_selection": 1,
                "total_selections": total_sel
            })
        except KeyError as e:
            logger.warning("Session data missing in make_bookmark: %s", e)
            return redirect('/')
        except Exception:
            logger.exception("Unexpected error in make_bookmark")
            return redirect('/')


def bookmark(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            song_name = data.get('song_name')
            selection_number = int(data.get('selection_number', 0))

            res_list = request.session.get('sorted_songs', [])
            res_list.append(song_name)
            if not song_name:
                return redirect('/')
                # return JsonResponse({'status': 'error', 'message': 'Empty Selection'}, status=400)
            request.session['sorted_songs'] = res_list
            request.session.modified = True

            # get current status from session
            total_selections = request.session.get('total_selections', 10)  # default : 10

            # check if selection is complete
            if selection_number >= total_selections:
                return JsonResponse({  # redirect if completed
                    'status': 'complete',
                    'message': '所有選擇已完成',
                    'redirect_url': '/result'
                })
            else:
                return JsonResponse({
                    'status': 'success',
                    'message': f'{selection_number} / {total_selections} : {song_name}',
                    'next_selection': selection_number + 1
                })
        except Exception:
            logger.exception("Error in views.bookmark(request)")
            return redirect('/')

    return redirect('/')


def see_full_result(request):
    if request.method == 'GET':
        try:
            full_list = request.session.get('full_sorted_songs')
            return render(request, "full_list.html", {
                'sorted_songs': full_list})
        except KeyError as e:
            logger.warning("Session data missing in make_bookmark: %s", e)
            return redirect('/')
        except Exception:
            logger.exception("Unexpected error in make_bookmark")
            return redirect('/')

    return redirect('/')
