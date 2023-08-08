from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView

from .forms import (
    PlayerModelForm,
)
from .models import Player
from ..games.models import GamePlayer


class PlayerListView(LoginRequiredMixin, TemplateView):
    """This view lists all players created by the current user."""

    template_name = "player_list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get all players created by the current user."""
        assert self.request.user.is_authenticated

        players = [
            {
                "full_name": player.full_name(),
                "inserted_at": player.inserted_at,
                "created_by_user": player.created_by_user,
                "id": player.id,
            }
            for player in Player.objects.filter(created_by_user=self.request.user)
            .exclude(is_deleted=True)
            .all()
        ]

        game_players = (
            GamePlayer.objects.select_related("player", "game")
            .filter(player__created_by_user=self.request.user)
            .exclude(player__is_deleted=True)
            .all()
        )

        for player in players:
            player["ongoing_games"] = game_players.filter(
                player__id=player["id"], game__is_ongoing=True
            ).count()
            player["completed_games"] = game_players.filter(
                player__id=player["id"], game__is_ongoing=False
            ).count()
            # TODO: Add games won.
            player["is_deletable"] = (
                player["ongoing_games"] == 0
                and player["created_by_user"] == self.request.user
                and player["id"] != self.request.user.player.id
            )

        return render(request, self.template_name, {"players": players})


class PlayerCreateView(LoginRequiredMixin, CreateView):
    """This view allows the user to create a new player."""

    template_name = "player_create.html"
    form_class = PlayerModelForm

    def form_valid(self, form: PlayerModelForm) -> HttpResponseRedirect:
        form.instance.created_by_user = self.request.user
        form.save()

        return HttpResponseRedirect("/players")


class PlayerDeleteView(LoginRequiredMixin, DeleteView, SuccessMessageMixin):
    """This view allows the user to delete a player."""

    object: Player  # work around python/mypy#9031
    model = Player
    success_url = "/players"
    template_name = "player_confirm_delete.html"

    def post(self, request, *args, **kwargs):
        """Override post to check the user can delete this player."""
        player = self.get_object()

        if self.request.user != player.created_by_user:
            return HttpResponseRedirect(f"/players/{player.id}/delete/error/")

        if player.user == self.request.user:
            return HttpResponseRedirect(f"/players/{player.id}/delete/error/")

        if (
            GamePlayer.objects.select_related("game")
            .filter(player=player)
            .filter(game__is_ongoing=True)
            .exists()
        ):
            return HttpResponseRedirect(f"/players/{player.id}/delete/error/")

        return super().post(request, *args, **kwargs)


class PlayerDeleteErrorView(LoginRequiredMixin, TemplateView):
    """This view is shown when a player cannot be deleted."""

    template_name = "player_delete_error.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get all players created by the current user."""
        assert self.request.user.is_authenticated

        player = get_object_or_404(Player, pk=kwargs["pk"])

        context = {
            "player": player,
            "player_is_user": player.user == self.request.user,
            "player_created_by_other_user": player.created_by_user != self.request.user,
            "player_in_ongoing_game": GamePlayer.objects.select_related("game")
            .filter(player=player)
            .filter(game__is_ongoing=True)
            .exists(),
        }

        return render(request, self.template_name, context)
