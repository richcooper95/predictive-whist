from django.db import transaction
from django.db.models import Max
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormView

from .forms import GameModelForm, GameRoundPredictionForm, GameRoundScoreForm, PlayerModelForm
from .models import GameRound, GameRoundGamePlayer, Player, Game, GamePlayer


# Create your views here.
def trump_suit_to_emoji(trump_suit):
    if trump_suit == "H":
        return '<span style="color: red">♥️</span>'

    if trump_suit == "D":
        return '<span style="color: red">♦️</span>'

    if trump_suit == "S":
        return "♠️"

    if trump_suit == "C":
        return "♣️"

    return "🃏"

def get_next_trump_suit(trump_suit):
    if trump_suit == "H":
        return "C"

    if trump_suit == "C":
        return "D"

    if trump_suit == "D":
        return "S"

    if trump_suit == "S":
        return "N"

    return "H"


class PlayerListView(LoginRequiredMixin, TemplateView):
    template_name = "player_list.html"

    def get(self, request, *args, **kwargs):
        players = Player.objects.filter(created_by_user=self.request.user).all()

        game_players = GamePlayer.objects.select_related("player", "game").filter(player__created_by_user=self.request.user).all()

        for player in players:
            player.ongoing_games = game_players.filter(
                player=player, game__is_ongoing=True
            ).count()
            player.completed_games = game_players.filter(
                player=player, game__is_ongoing=False
            ).count()
            # TODO: Add games won.

        return render(request, self.template_name, {"players": players})


class PlayerCreateView(LoginRequiredMixin, CreateView):
    template_name = "player_create.html"
    form_class = PlayerModelForm

    def form_valid(self, form):
        form.instance.created_by_user = self.request.user
        form.save()

        return HttpResponseRedirect("/players")


class PlayerDeleteView(LoginRequiredMixin, DeleteView, SuccessMessageMixin):
    model = Player
    success_url = "/players"
    # TODO: This doesn't work. Why?
    success_message = "Player deleted successfully."
    template_name = "player_confirm_delete.html"


class GameListView(LoginRequiredMixin, TemplateView):
    template_name = "game_list.html"

    def get(self, request, *args, **kwargs):
        games = Game.objects.filter(created_by_user=self.request.user).all()
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

        return render(
            request,
            self.template_name,
            {
                "ongoing_games": ongoing_games,
                "completed_games": completed_games,
            },
        )


class GameCreateView(LoginRequiredMixin, CreateView):
    template_name = "game_create.html"
    form_class = GameModelForm

    def get_form_kwargs(self):
        kwargs = super(GameCreateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user_player_count"] = Player.objects.filter(
            created_by_user=self.request.user
        ).count()

        return context

    def form_valid(self, form):
        with transaction.atomic():
            # First, save the game so we can get an ID.
            game = Game.objects.create(
                name=form.cleaned_data["name"],
                is_ongoing=True,
                correct_prediction_points=form.cleaned_data["correct_prediction_points"],
                starting_round_card_number=form.cleaned_data["starting_round_card_number"],
                number_of_decks=form.cleaned_data["number_of_decks"],
                created_by_user=self.request.user,
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


class GameDeleteView(LoginRequiredMixin, DeleteView, SuccessMessageMixin):
    model = Game
    success_url = "/games"
    # TODO: This doesn't work. Why?
    success_message = "Game deleted successfully."
    template_name = "game_confirm_delete.html"


class GameShowView(LoginRequiredMixin, TemplateView):
    template_name = "game_show.html"

    def get(self, request, *args, **kwargs):
        game = get_object_or_404(Game, id=self.kwargs["pk"])

        if not game.visible_to(self.request.user):
            return HttpResponseForbidden()

        game_players = GamePlayer.objects.select_related("game", "player").filter(game=game).all()
        max_score = game_players.aggregate(Max("score"))["score__max"]
        winning_players = ", ".join(
            game_players.filter(score=max_score).values_list("player__name", flat=True)
        )
        latest_game_round = GameRound.objects.filter(game=game).order_by("round_number").last()

        dealer_player_number = latest_game_round.round_number % len(game_players) + 1

        return render(
            request,
            self.template_name,
            {
                "game": game,
                "game_players": game_players,
                "game_player_names": ", ".join(
                    game_players.values_list("player__name", flat=True)
                ),
                "winning_players": winning_players,
                "latest_game_round": latest_game_round,
                "trump_suit": trump_suit_to_emoji(latest_game_round.trump_suit),
                "dealer_name": game_players.get(player_number=dealer_player_number).player.name,
            },
        )


class GameRoundPredictionView(LoginRequiredMixin, FormView):
    template_name = "game_round_bids.html"
    form_class = GameRoundPredictionForm

    def get(self, request, *args, **kwargs):
        game_round = get_object_or_404(GameRound, pk=self.kwargs["round_id"])

        if not game_round.visible_to(self.request.user):
            return HttpResponseForbidden()

        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.path

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        game_round = get_object_or_404(GameRound, pk=self.kwargs["round_id"])

        round_players = list(GameRoundGamePlayer.objects.select_related("game_round", "game_player").filter(game_round=game_round).order_by("game_player__player_number").all())

        starting_player_idx = game_round.round_number % len(round_players) + 1

        round_players = round_players[starting_player_idx:] + round_players[:starting_player_idx]

        kwargs["round_players"] = round_players
        kwargs["card_number"] = game_round.card_number

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(GameRoundPredictionView, self).get_context_data(**kwargs)

        game = get_object_or_404(Game, id=self.kwargs["game_id"])
        game_players = GamePlayer.objects.select_related("game", "player").filter(game=game).all()
        max_score = game_players.aggregate(Max("score"))["score__max"]
        latest_game_round = GameRound.objects.filter(game=game).order_by("round_number").last()
        round_players = list(GameRoundGamePlayer.objects.select_related("game_round", "game_player").filter(game_round=latest_game_round).order_by("game_player__player_number").all())

        starting_player_idx = latest_game_round.round_number % len(game_players) + 1

        round_players = round_players[starting_player_idx:] + round_players[:starting_player_idx]

        dealer_player_number = latest_game_round.round_number % len(game_players) + 1

        context["game"] = game
        context["game_players"] = game_players
        context["game_player_names"] = ", ".join(
                    game_players.values_list("player__name", flat=True)
                )
        context["winning_players"] = ", ".join(
                    game_players.filter(score=max_score).values_list("player__name", flat=True)
                )
        context["latest_game_round"] = latest_game_round
        context["trump_suit"] = trump_suit_to_emoji(latest_game_round.trump_suit)
        context["dealer_name"] = game_players.get(
                    player_number=dealer_player_number
                ).player.name
        context["round_players"] = round_players

        return context

    def form_valid(self, form):
        with transaction.atomic():
            game_round = get_object_or_404(GameRound, pk=self.kwargs["round_id"])

            for round_player in form.cleaned_data:
                player_number = round_player.split("_")[-1]
                tricks_predicted = form.cleaned_data[round_player]
                if tricks_predicted is not None:
                    game_round_game_player, _ = GameRoundGamePlayer.objects.get_or_create(
                        game_round=game_round, game_player__player_number=player_number,
                        defaults={"tricks_predicted": tricks_predicted}
                    )
                    game_round_game_player.tricks_predicted = tricks_predicted
                    game_round_game_player.save()

            total_tricks_predicted = sum(
                round_player.tricks_predicted for round_player in game_round.gameroundgameplayer_set.all()
            )
            game_round.total_tricks_predicted = total_tricks_predicted
            game_round.save()

        return HttpResponseRedirect(f"/games/{game_round.game.id}/round/{game_round.id}/scores/")


class GameRoundScoreView(LoginRequiredMixin, FormView):
    template_name = "game_round_scores.html"
    form_class = GameRoundScoreForm

    def get_success_url(self):
        return self.request.path

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        game_round = get_object_or_404(GameRound, pk=self.kwargs["round_id"])

        round_players = list(GameRoundGamePlayer.objects.select_related("game_round", "game_player").filter(game_round=game_round).order_by("game_player__player_number").all())

        starting_player_idx = game_round.round_number % len(round_players) + 1

        round_players = round_players[starting_player_idx:] + round_players[:starting_player_idx]

        kwargs["round_players"] = round_players
        kwargs["card_number"] = game_round.card_number

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(GameRoundScoreView, self).get_context_data(**kwargs)

        game = get_object_or_404(Game, id=self.kwargs["game_id"])
        game_players = GamePlayer.objects.select_related("game", "player").filter(game=game).all()
        max_score = game_players.aggregate(Max("score"))["score__max"]
        latest_game_round = GameRound.objects.filter(game=game).order_by("round_number").last()
        round_players = list(GameRoundGamePlayer.objects.select_related("game_round", "game_player").filter(game_round=latest_game_round).order_by("game_player__player_number").all())

        starting_player_idx = latest_game_round.round_number % len(game_players) + 1

        round_players = round_players[starting_player_idx:] + round_players[:starting_player_idx]

        dealer_player_number = latest_game_round.round_number % len(game_players) + 1

        context["game"] = game
        context["game_players"] = game_players
        context["game_player_names"] = ", ".join(
                    game_players.values_list("player__name", flat=True)
                )
        context["winning_players"] = ", ".join(
                    game_players.filter(score=max_score).values_list("player__name", flat=True)
                )
        context["latest_game_round"] = latest_game_round
        context["trump_suit"] = trump_suit_to_emoji(latest_game_round.trump_suit)
        context["dealer_name"] = game_players.get(
                    player_number=dealer_player_number
                ).player.name
        context["round_players"] = round_players

        return context

    def form_valid(self, form):
        with transaction.atomic():
            game_round = get_object_or_404(GameRound, pk=self.kwargs["round_id"])

            for round_player in form.cleaned_data:
                player_number = round_player.split("_")[-1]
                tricks_won = form.cleaned_data[round_player]
                if tricks_won is not None:
                    game_round_game_player, _ = GameRoundGamePlayer.objects.get_or_create(
                        game_round=game_round, game_player__player_number=player_number,
                        defaults={"tricks_won": tricks_won}
                    )
                    game_round_game_player.tricks_won = tricks_won

                    game_round_game_player.game_player.score += tricks_won

                    if game_round_game_player.tricks_predicted == game_round_game_player.tricks_won:
                        game_round_game_player.game_player.score += game_round.game.correct_prediction_points

                    game_round_game_player.save()
                    game_round_game_player.game_player.save()

            # Now we need to figure out how many cards to deal for the next round.
            if game_round.game.card_number_descending:
                if game_round.card_number == 1:
                    game_round.game.card_number_descending = False
                    game_round.game.save()
                    next_round_card_number = 2
                else:
                    next_round_card_number = game_round.card_number - 1
            else:
                next_round_card_number = game_round.card_number + 1

            # If the next round card number is higher than the starting round card number,
            # then the game is over.
            if next_round_card_number > game_round.game.starting_round_card_number:
                game_round.game.is_ongoing = False
                game_round.game.save()



                # And we need to redirect to the game's homepage.
                return HttpResponseRedirect(f"/games/{game_round.game.id}")

            # Then we create the next round of the game, with the next trump suit and the
            # new card number.
            next_round = GameRound.objects.create(
                game=game_round.game,
                round_number=game_round.round_number + 1,
                trump_suit=get_next_trump_suit(game_round.trump_suit),
                card_number=next_round_card_number,
            )

            # Now set the game_players of the new game_round to the game_players we created
            # earlier. This will also create the GameRoundGamePlayer objects.
            next_round.game_players.set(game_round.game_players.all())

            next_round.save()

        return HttpResponseRedirect(f"/games/{game_round.game.id}")
