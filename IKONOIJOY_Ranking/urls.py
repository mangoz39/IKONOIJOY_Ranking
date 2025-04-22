"""
URL configuration for IKONOIJOY_Ranking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from ranking.views import (index, start_ranking, rank, choose_song, result, see_full_result,
                           oshi_statistics_view, record, bookmark, make_bookmark)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('home', index),
    path('start_ranking', start_ranking, name='start_ranking'),
    path('rank', rank, name='rank'),
    path('bookmark', bookmark, name='bookmark'),
    path('make_bookmark', make_bookmark, name='make_bookmark'),
    path('choose_song', choose_song),
    path('result', result, name='result'),
    path('record', record, name='record'),
    path('full_list', see_full_result, name='full_list'),
    path('api/oshi-statistics', oshi_statistics_view, name='oshi_statistics')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)