import random

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .function import ranking  # 引入排序類
from .files import equalsong
import json

# Global Variables
song_list = equalsong.testlist
full_list = equalsong.equal_song
rank_list = []
result = []


def index(request):
    song = random.sample(range(len(full_list)), 10)
    rank_list = []
    for s in song:
        rank_list.append(full_list[s])
    request.session["songs"] = song
    sorted_songs = request.session.get("sorted_songs", [])
    if sorted_songs:
        for rk in sorted_songs:
            result.append(full_list[rk].getName())
    return render(request, "index.html")


def start_ranking(request):
    """初始化排名"""
    songs = request.session.get("songs", [])
    if not songs:
        return redirect("/home/")

    ranker = ranking.SongRanker(songs)  # 建立 ranking 物件
    request.session["ranker"] = ranker.to_dict()  # 存入 session
    request.session["sorted_songs"] = []
    return redirect("/ranking_page/")


def ranking_page(request):
    try:
        ranker_data = request.session.get("ranker")
    except:
        return JsonResponse({"error": "Ranking session not found"}, status=400)
    # 使用 from_dict 重新建立 SongRanker 物件
    songs = request.session.get("songs", [])
    ranker = ranking.SongRanker.from_dict(ranker_data, songs)
    song1, song2 = ranker.get_current_pair()
    request.session["ranker"] = ranker.to_dict()

    if song1 is None or song2 is None:
        request.session["sorted_songs"] = ranker.temp_list[0]
        return redirect("/home/")

    # need fix, pass the ranker to choose song
    return render(request, "rank.html", {
        "song1": full_list[ranker.tmp_left[0]].getName(),
        "song2": full_list[ranker.tmp_right[0]].getName()
    })


@csrf_exempt
def choose_song(request):

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
        song1, song2 = ranker.get_current_pair()

        request.session["ranker"] = ranker.to_dict()

        if is_finished:
            request.session["sorted_songs"] = ranker.temp_list[0]
            return JsonResponse({"finished": True})

        return JsonResponse({
            "finished": False,
            "song1": full_list[ranker.tmp_left[0]].getName(),
            "song2": full_list[ranker.tmp_right[0]].getName()
        })

    return JsonResponse({"finished": False})
