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
from django.contrib.auth.views import PasswordResetView
from django.urls import include, path, re_path

from apps.games.views import (
    GameDeleteView,
    GameRoundPredictionView,
    GameRoundScoreView,
    GameShowView,
    GameListView,
    GameCreateView,
)
from apps.home.views import HomeView, InfoView, PrivacyPolicyView, RulesView
from apps.players.views import (
    PlayerCreateView,
    PlayerDeleteView,
    PlayerDeleteErrorView,
    PlayerListView,
)
from apps.users.views import UserCreateView, UserUpdateView
from apps.users.forms import UserCreateForm, UserUpdateForm

# pylint: disable=line-too-long
urlpatterns = [
    path(
        "accounts/register/",
        UserCreateView.as_view(form_class=UserCreateForm),
        name="django_registration_register",
    ),
    path(
        "accounts/profile/",
        UserUpdateView.as_view(form_class=UserUpdateForm),
        name="user_profile",
    ),
    path("accounts/", include("django_registration.backends.one_step.urls")),
    path(
        "accounts/password_reset/",
        PasswordResetView.as_view(
            html_email_template_name="registration/password_reset_email.html"
        ),
        name="password_reset"
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", HomeView.as_view(), name="home"),
    path("info/", InfoView.as_view(), name="info"),
    path("rules/", RulesView.as_view(), name="rules"),
    path("players/", PlayerListView.as_view(), name="players"),
    path("players/new/", PlayerCreateView.as_view(), name="player_create"),
    re_path(
        r"^players/(?P<pk>pla_[0-9a-zA-Z]+)/delete/$",
        PlayerDeleteView.as_view(),
        name="player_delete",
    ),
    re_path(
        r"^players/(?P<pk>pla_[0-9a-zA-Z]+)/delete/error/$",
        PlayerDeleteErrorView.as_view(),
        name="player_delete_error",
    ),
    path("games/", GameListView.as_view(), name="games"),
    re_path(
        r"^games/(?P<pk>gam_[0-9a-zA-Z]+)/$", GameShowView.as_view(), name="game_show"
    ),
    path("games/new/", GameCreateView.as_view(), name="game_create"),
    re_path(
        r"^games/delete/(?P<pk>gam_[0-9a-zA-Z]+)/$",
        GameDeleteView.as_view(),
        name="game_delete",
    ),
    re_path(
        r"^games/(?P<game_id>gam_[0-9a-zA-Z]+)/round/(?P<round_number>[0-9]+)/bids/(?P<player_number>[0-9]+)/$",
        GameRoundPredictionView.as_view(),
        name="game_round_bids",
    ),
    re_path(
        r"games/(?P<game_id>gam_[0-9a-zA-Z]+)/round/(?P<round_number>[0-9]+)/bids/",
        GameRoundPredictionView.as_view(),
        name="game_round_bids",
    ),
    re_path(
        r"games/(?P<game_id>gam_[0-9a-zA-Z]+)/round/(?P<round_number>[0-9]+)/scores/(?P<player_number>[0-9]+)/",
        GameRoundScoreView.as_view(),
        name="game_round_scores",
    ),
    re_path(
        r"games/(?P<game_id>gam_[0-9a-zA-Z]+)/round/(?P<round_number>[0-9]+)/scores/",
        GameRoundScoreView.as_view(),
        name="game_round_scores",
    ),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy"),
    path("admin/", admin.site.urls),
]
