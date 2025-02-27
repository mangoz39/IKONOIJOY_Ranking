import random

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .function import ranking, plot  # 引入排序類
from .files import songs as sg
import json

# Global Variables
song_list = []
song_count = 0
rand_list = []
rank_list = []
result_list = []
oshi_list = []


def index(request):
    request.session.flush()
    return render(request, "index.html")


def start_ranking(request):
    request.session.flush()
    global song_list, song_count, rand_list, rank_list, result, oshi_list
    song_list = []
    song_count = 0
    rand_list = []
    rank_list = []
    result = []
    oshi_list = []
    if request.method == 'POST':
        list_ref = request.POST.get('list_ref', '')
        oshi1 = request.POST.get('oshi1', '')
        oshi2 = request.POST.get('oshi2', '')
        oshi3 = request.POST.get('oshi3', '')
        print("所有 POST 參數:", request.POST)

        match list_ref:
            case '1':
                song_list = sg.equallove_song
                song_count = sg.equal_total
            case '10':
                song_list = sg.notequalme_song
                song_count = sg.not_equal_me_total
            case '11':
                song_list = sg.ikonoi_song
                song_count = sg.ikonoi_total
            case '100':
                song_list = sg.nearlyequaljoy_song
                song_count = sg.nearly_equal_joy_total
            case '101':
                song_list = sg.ikojoy_song
                song_count = sg.ikojoy_total
            case '110':
                song_list = sg.noijoy_song
                song_count = sg.noijoy_total
            case '111':
                song_list = sg.ikonoijoy_song
                song_count = sg.ikonoijoy_total
            case _:
                return redirect('home/')

        for i in range(song_count):
            rand_list.append(i)

        random.shuffle(rand_list)
        request.session["songs"] = rand_list
        oshi_list.append([oshi1, oshi2, oshi3])

        ranker = ranking.SongRanker(rand_list)  # 建立 ranking 物件
        request.session["ranker"] = ranker.to_dict()  # 存入 session
        request.session["sorted_songs"] = []

        request.session['can_access'] = '1'
        return redirect("ranking_page")

    return redirect('home')


def ranking_page(request):
    permission = request.session.get("can_access")
    if permission == '1':
        try:
            ranker_data = request.session.get("ranker")
        except:
            return JsonResponse({"error": "Access Denied"}, status=400)

        # 使用 from_dict 重新建立 SongRanker 物件
        songs = request.session.get("songs", [])
        ranker = ranking.SongRanker.from_dict(ranker_data, songs)
        song1, song2 = ranker.get_current_pair()
        request.session["ranker"] = ranker.to_dict()

        if song1 is None or song2 is None:
            request.session["sorted_songs"] = ranker.temp_list[0]
            return redirect("/home/")

        return render(request, "ranking2.html", {
            "finished": False,
            "song1": song_list[ranker.tmp_left[0]].getName(),
            "song2": song_list[ranker.tmp_right[0]].getName(),
            "song1_youtube_id": song_list[ranker.tmp_left[0]].getID(),
            "song2_youtube_id": song_list[ranker.tmp_right[0]].getID(),
            "song1_color": song_list[ranker.tmp_left[0]].getGroup(),
            "song2_color": song_list[ranker.tmp_right[0]].getGroup()
        })
    else:
        return JsonResponse({"error": "Access Denied"}, status=400)


@csrf_exempt
def choose_song(request):
    global result_list
    if request.method == "POST":
        try:
            ranker_data = request.session.get("ranker")
        except:
            return JsonResponse({"error": "Ranking session not found"}, status=400)
        # 使用 from_dict 重新建立 SongRanker 物件
        songs = request.session.get("songs", [])
        ranker = ranking.SongRanker.from_dict(ranker_data, songs)

        data = json.loads(request.body)
        choice = data.get("choice")

        is_finished = ranker.choose(choice)

        # 後面要修，避免直接拿tmp會報錯
        song1, song2 = ranker.get_current_pair()

        request.session["ranker"] = ranker.to_dict()

        if is_finished:
            tmp_res = ranker.temp_list[0]
            tmp_ses = []
            for s in tmp_res[:10]:
                result_list.append(song_list[s])

            for sg in result_list:
                tmp_ses.append(sg.getName())
            request.session["sorted_songs"] = tmp_ses
            return JsonResponse({"finished": True})

        return JsonResponse({
            "finished": False,
            "song1": song_list[ranker.tmp_left[0]].getName(),
            "song2": song_list[ranker.tmp_right[0]].getName(),
            "song1_youtube_id": song_list[ranker.tmp_left[0]].getID(),
            "song2_youtube_id": song_list[ranker.tmp_right[0]].getID(),
            "song1_color": song_list[ranker.tmp_left[0]].getGroup(),
            "song2_color": song_list[ranker.tmp_right[0]].getGroup()
        })

    return JsonResponse({"finished": False})


def result(request):
    plot_pend = request.session.get('sorted_songs')
    img = plot.plot_rank(plot_pend)
    return render(request, "result.html", {
        'base64_image': img,
        'image_type': 'image/png'})
