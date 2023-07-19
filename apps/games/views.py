from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import NewGameForm
from .models import Player, Game, GamePlayer

# Create your views here.
class PlayersView(TemplateView, LoginRequiredMixin):
    template_name = "players.html"

    def get(self, request, *args, **kwargs):
        players = Player.objects.all()

        games = GamePlayer.objects.select_related("player")

        for player in players:
            player.ongoing_games = games.filter(player=player, game__is_ongoing=True).count()
            player.completed_games = games.filter(player=player, game__is_ongoing=False).count()


        return render(request, self.template_name, {"players": players})

class GamesView(TemplateView, LoginRequiredMixin):
    template_name = "games.html"

    def get(self, request, *args, **kwargs):
        games = Game.objects.all()

        game_players = GamePlayer.objects.select_related("game", "player")

        for game in games:
            game.game_players_count = game_players.filter(game=game).count()
            winning_game_player = game_players.filter(game=game).order_by("-score").first()

            if winning_game_player is not None and not game.is_ongoing:
                game.winning_player = winning_game_player.player.name
            else:
                game.winning_player = "TBC"

        return render(request, self.template_name, {"games": games})


class NewGameView(FormView, LoginRequiredMixin):
    template_name = "new_game.html"
    form_class = NewGameForm
    success_url = "/"

    def form_valid(self, form):
        form.save()

        return super().form_valid(form)
