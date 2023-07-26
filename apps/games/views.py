from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView

from .forms import GameModelForm, PlayerModelForm
from .models import GameRound, GameRoundGamePlayer, Player, Game, GamePlayer


# Create your views here.
class PlayersView(TemplateView, LoginRequiredMixin):
    template_name = "player_list.html"

    def get(self, request, *args, **kwargs):
        players = Player.objects.all()

        games = GamePlayer.objects.select_related("player")

        for player in players:
            player.ongoing_games = games.filter(
                player=player, game__is_ongoing=True
            ).count()
            player.completed_games = games.filter(
                player=player, game__is_ongoing=False
            ).count()

        return render(request, self.template_name, {"players": players})


class PlayerCreateView(CreateView, LoginRequiredMixin):
    template_name = "player_create.html"
    form_class = PlayerModelForm

    def form_valid(self, form):
        form.instance.created_by_user = self.request.user
        form.save()

        return HttpResponseRedirect("/players")


class PlayerDeleteView(DeleteView, LoginRequiredMixin, SuccessMessageMixin):
    model = Player
    success_url = "/players"
    # TODO: This doesn't work. Why?
    success_message = "Player deleted successfully."
    template_name = "player_confirm_delete.html"


class GamesView(TemplateView, LoginRequiredMixin):
    template_name = "game_list.html"

    def get(self, request, *args, **kwargs):
        games = Game.objects.all()
        game_players = GamePlayer.objects.select_related("game", "player").all()

        ongoing_games = []
        completed_games = []

        for game in games:
            game.player_names = ", ".join(
                game_players.filter(game=game).values_list("player__name", flat=True)
            )

            winning_game_player = (
                game_players.filter(game=game).order_by("-score").first()
            )

            if winning_game_player is not None and not game.is_ongoing:
                game.winning_player = winning_game_player.player.name
            else:
                game.winning_player = "TBC"

            if game.is_ongoing:
                ongoing_games.append(game)
            else:
                completed_games.append(game)

        print(ongoing_games)
        print(completed_games)
        return render(
            request,
            self.template_name,
            {
                "ongoing_games": ongoing_games,
                "completed_games": completed_games,
            },
        )


class GameCreateView(CreateView, LoginRequiredMixin):
    template_name = "game_create.html"
    form_class = GameModelForm

    def form_valid(self, form):
        # First, save the game so we can get an ID.
        game = Game.objects.create(
            name=form.cleaned_data["name"],
            is_ongoing=True,
            correct_prediction_points=form.cleaned_data["correct_prediction_points"],
            starting_round_card_number=form.cleaned_data["starting_round_card_number"],
            number_of_decks=form.cleaned_data["number_of_decks"],
        )

        # Then, save the players by creating a GamePlayer object for each, making sure we
        # set the player_number correctly.
        game_players = [
            GamePlayer.objects.create(
                game=game,
                player=player,
                player_number=idx + 1,
            )
            for idx, player in enumerate(form.cleaned_data["players"])
        ]

        # Then we create the first round of the game, with H as the first trump
        # suit, and the card number as the starting round card number.
        game_round = GameRound.objects.create(
            game=game,
            round_number=1,
            trump_suit="H",
            card_number=game.starting_round_card_number,
        )

        # Now set the game_players of the game_round to the game_players we created
        # earlier.
        game_round.game_players.set(game_players)

        return HttpResponseRedirect(f"/games/{game.id}")


class GameDeleteView(DeleteView, LoginRequiredMixin, SuccessMessageMixin):
    model = Game
    success_url = "/games"
    # TODO: This doesn't work. Why?
    success_message = "Game deleted successfully."
    template_name = "game_confirm_delete.html"


class GameShowView(TemplateView, LoginRequiredMixin):
    template_name = "game_show.html"

    def trump_suit_to_emoji(self, trump_suit):
        if trump_suit == "H":
            return '<span style="color: red">♥️</span>'

        if trump_suit == "D":
            return '<span style="color: red">♦️</span>'

        if trump_suit == "S":
            return "♠️"

        if trump_suit == "C":
            return "♣️"

        return "🃏"

    def get(self, request, *args, **kwargs):
        game = get_object_or_404(Game, id=self.kwargs["pk"])
        game_players = GamePlayer.objects.select_related("game", "player").filter(game=game).all()
        latest_game_round = GameRound.objects.filter(game=game).order_by("round_number").last()

        return render(
            request,
            self.template_name,
            {
                "game": game,
                "game_players": game_players,
                "game_player_names": ", ".join(
                    game_players.values_list("player__name", flat=True)
                ),
                "current_winning_player": game_players.order_by("-score").first(),
                "latest_game_round": latest_game_round,
                "trump_suit": self.trump_suit_to_emoji(latest_game_round.trump_suit),
                "dealer_name": game_players.get(player_number=latest_game_round.round_number%len(game_players)).player.name,
            },
        )
