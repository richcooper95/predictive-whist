"""
URL configuration for predictive_whist project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path

from apps.games.views import (
    GameDeleteView,
    GameRoundPredictionView,
    GameRoundScoreView,
    GameShowView,
    GameListView,
    GameCreateView,
    PlayerCreateView,
    PlayerDeleteView,
    PlayerListView,
)
from apps.home.views import HomeView

urlpatterns = [
    path("accounts/", include("django_registration.backends.one_step.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", HomeView.as_view(), name="home"),
    path("players/", PlayerListView.as_view(), name="players"),
    path("players/new/", PlayerCreateView.as_view(), name="player_create"),
    path("players/delete/<int:pk>/", PlayerDeleteView.as_view(), name="player_delete"),
    path("games/", GameListView.as_view(), name="games"),
    path("games/<int:pk>/", GameShowView.as_view(), name="game_show"),
    path("games/new/<", GameCreateView.as_view(), name="game_create"),
    path("games/delete/<int:pk>/", GameDeleteView.as_view(), name="game_delete"),
    path("games/<int:game_id>/round/<int:round_id>/bids/", GameRoundPredictionView.as_view(), name="game_round_bids"),
    path("games/<int:game_id>/round/<int:round_id>/scores/", GameRoundScoreView.as_view(), name="game_round_scores"),
    path("admin/", admin.site.urls),
]
