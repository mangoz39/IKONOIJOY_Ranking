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
from ranking.views import index, start_ranking, ranking_page, choose_song

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', index),
    path('start_ranking/', start_ranking),
    path('ranking_page/', ranking_page),
    path('choose_song/', choose_song)
]
