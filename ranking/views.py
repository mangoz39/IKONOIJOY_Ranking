import json
import random

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .function import ranking, plot  # 引入排序類
from .files import songs as sg


def index(request):
    request.session.flush()
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
    rand_list = []
    if request.method == 'POST':
        list_ref = request.POST.get('list_ref', '')
        oshi1 = request.POST.get('oshi1', '')
        oshi2 = request.POST.get('oshi2', '')
        oshi3 = request.POST.get('oshi3', '')
        request.session['oshi'] = [oshi1, oshi2, oshi3]
        print("所有 POST 參數:", request.POST)

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
                return redirect('home/')

        for i in range(song_count):
            rand_list.append(i)

        random.shuffle(rand_list)
        request.session["songs"] = rand_list
        request.session['song_list'] = song_list
        request.session['song_count'] = song_count

        ranker = ranking.SongRanker(rand_list)  # 建立 ranking 物件
        request.session["ranker"] = ranker.to_dict()  # 存入 session
        request.session["sorted_songs"] = []

        request.session['can_access'] = '1'
        return redirect("ranking_page")

    return redirect('home')


def ranking_page(request):
    permission = request.session.get("can_access")
    song_list = sg.slist[request.session.get('song_list')]
    if permission == '1':
        ranker_data = request.session.get("ranker")
        if ranker_data is None:
            return JsonResponse({"error": "Access Denied"}, status=400)

        # 使用 from_dict 重新建立 SongRanker 物件
        songs = request.session.get("songs", [])
        ranker = ranking.SongRanker.from_dict(ranker_data, songs)
        song_left, song_right = ranker.get_current_pair()
        if song_left == 0 and song_right == 0:
            return JsonResponse({"error": "Access Denied"}, status=400)

        request.session["ranker"] = ranker.to_dict()

        return render(request, "ranking2.html", {
            "finished": False,
            "song1": song_list[song_left].getName(),
            "song2": song_list[song_right].getName(),
            "song1_youtube_id": song_list[song_left].getID(),
            "song2_youtube_id": song_list[song_right].getID(),
            "song1_color": song_list[song_left].getGroup(),
            "song2_color": song_list[song_right].getGroup()
        })
    else:
        return JsonResponse({"error": "Access Denied"}, status=400)


@csrf_exempt
def choose_song(request):
    song_list = sg.slist[request.session.get('song_list')]
    if request.method == "POST":
        ranker_data = request.session.get("ranker")
        if ranker_data is None:
            return JsonResponse({"error": "Access Denied"}, status=400)

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
            result_list = []
            if request.session.get('song_count') > 55:
                k = 10
            else:
                k = 12
            for s in tmp_res[:k]:
                result_list.append(song_list[s])

            for songs in result_list:
                tmp_ses.append(songs.getName())
            request.session["sorted_songs"] = tmp_ses
            return JsonResponse({"finished": True})

        song_left, song_right = ranker.get_current_pair()
        if song_left == 0 and song_right == 0:
            return JsonResponse({"error": "Access Denied"}, status=400)

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
        request.session.get('sorted_songs'),
        request.session.get('song_count'),
        request.session.get('oshi', ['', '', '']))
    img = plot.plot_rank(plot_pend, song_count, oshi_list)
    return render(request, "result.html", {
        'base64_image': img,
        'image_type': 'image/png'})
