from functools import reduce
from typing import Dict, List
from django.db import transaction
from django.db.models import Max, QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormView

from .forms import (
    GameModelForm,
    GameRoundPredictionForm,
    GameRoundScoreForm,
    PlayerModelForm,
)
from .models import GameRound, GamePlayerGameRound, Player, Game, GamePlayer


TRUMP_SUIT_TO_EMOJI = {
    "H": '<span style="color: red">♥️</span>',
    "D": '<span style="color: red">♦️</span>',
    "S": "♠️",
    "C": "♣️",
    "N": "🃏",
}

NEXT_TRUMP_SUIT = {
    "H": "C",
    "C": "D",
    "D": "S",
    "S": "N",
    "N": "H",
}


class PlayerListView(LoginRequiredMixin, TemplateView):
    """This view lists all players created by the current user."""

    template_name = "player_list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get all players created by the current user."""
        players = Player.objects.filter(created_by_user=self.request.user).all()

        game_players = (
            GamePlayer.objects.select_related("player", "game")
            .filter(player__created_by_user=self.request.user)
            .all()
        )

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
    """This view allows the user to create a new player."""

    template_name = "player_create.html"
    form_class = PlayerModelForm

    def form_valid(self, form: PlayerModelForm) -> HttpResponseRedirect:
        form.instance.created_by_user = self.request.user
        form.save()

        return HttpResponseRedirect("/players")


class PlayerDeleteView(LoginRequiredMixin, DeleteView, SuccessMessageMixin):
    """This view allows the user to delete a player."""

    model = Player
    success_url = "/players"
    # TODO: This doesn't work. Why?
    success_message = "Player deleted successfully."
    template_name = "player_confirm_delete.html"


class GameListView(LoginRequiredMixin, TemplateView):
    """This view lists all games created by the current user."""

    template_name = "game_list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        games = Game.objects.filter(created_by_user=self.request.user).all()
        game_players = GamePlayer.objects.select_related("game", "player").all()

        ongoing_games = []
        completed_games = []

        for game in games:
            game.player_names = ", ".join(
                game_players.filter(game=game).values_list(
                    "unique_display_name", flat=True
                )
            )

            winning_game_player = (
                game_players.filter(game=game).order_by("-score").first()
            )

            if winning_game_player is not None and not game.is_ongoing:
                game.winning_player = winning_game_player.unique_display_name
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
    """This view allows the user to create a new game."""

    template_name = "game_create.html"
    form_class = GameModelForm

    def get_form_kwargs(self) -> Dict:
        kwargs = super(GameCreateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)

        context["user_player_count"] = Player.objects.filter(
            created_by_user=self.request.user
        ).count()

        return context

    def form_valid(self, form: GameModelForm) -> HttpResponseRedirect:
        """Save the game and redirect to the game page.

        Creates the game, the game players, the first round. Adds the game players to the
        first round, creating a GamePlayerGameRound object for each.

        Args:
            form (GameModelForm): The form containing the game data.

        Returns:
            HttpResponseRedirect: Redirects to the page for the newly created game.
        """
        with transaction.atomic():
            # First, save the game so we can get an ID.
            game = Game.objects.create(
                name=form.cleaned_data["name"],
                is_ongoing=True,
                correct_prediction_points=form.cleaned_data[
                    "correct_prediction_points"
                ],
                starting_round_card_number=form.cleaned_data[
                    "starting_round_card_number"
                ],
                number_of_decks=form.cleaned_data["number_of_decks"],
                created_by_user=self.request.user,
            )

            players = list(form.cleaned_data["players"])

            # Then, save the players by creating a GamePlayer object for each, making sure we
            # set the player_number correctly.
            # TODO: Enable users to choose the player order in the form.
            game_players = [
                GamePlayer.objects.create(
                    game=game,
                    player=player,
                    player_number=idx + 1,
                    unique_display_name=player.unique_display_name(players),
                )
                for idx, player in enumerate(players)
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
    """This view allows the user to delete a game."""

    model = Game
    success_url = "/games"
    # TODO: This doesn't work. Why?
    success_message = "Game deleted successfully."
    template_name = "game_confirm_delete.html"


class GameShowView(LoginRequiredMixin, TemplateView):
    """This view shows the details of a game and enables gameplay."""

    template_name = "game_show.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        game = get_object_or_404(Game, id=self.kwargs["pk"])

        if not game.visible_to(self.request.user):
            return HttpResponseForbidden()

        game_players = (
            GamePlayer.objects.select_related("game", "player")
            .filter(game=game)
            .order_by("player_number")
            .all()
        )
        max_score = game_players.aggregate(Max("score"))["score__max"]
        winning_players = ", ".join(
            game_players.filter(score=max_score).values_list(
                "unique_display_name", flat=True
            )
        )
        latest_game_round = (
            GameRound.objects.filter(game=game).order_by("round_number").last()
        )
        round_players = (
            GamePlayerGameRound.objects.select_related("game_round", "game_player")
            .filter(game_round__game=game)
            .order_by("game_round__round_number", "game_player__player_number")
            .all()
        )
        last_round_to_show = (
            latest_game_round.round_number
            if latest_game_round.total_tricks_predicted is not None
            else latest_game_round.round_number - 1
        )

        # TODO: Neaten this up, it's a bit of a mess.
        game_rounds = [
            (
                str(round_number),
                [
                    {
                        "tricks_won": round_player.tricks_won
                        if round_player.tricks_won is not None
                        else "",
                        "tricks_predicted": round_player.tricks_predicted
                        if round_player.tricks_predicted is not None
                        else "",
                        "score": (
                            (round_player.tricks_won or 0)
                            + (
                                game.correct_prediction_points
                                if round_player.tricks_predicted
                                == round_player.tricks_won
                                else 0
                            )
                        )
                        if round_player.tricks_won is not None
                        else "",
                        "player_number": round_player.game_player.player_number,
                    }
                    for round_player in round_players
                    if round_player.game_round.round_number == round_number
                ],
            )
            for round_number in range(last_round_to_show, 0, -1)
        ]

        dealer_player_number = latest_game_round.round_number % len(game_players) + 1

        return render(
            request,
            self.template_name,
            {
                "game": game,
                "game_players": game_players,
                "game_player_names": ", ".join(
                    game_players.values_list("unique_display_name", flat=True)
                ),
                "winning_players": winning_players,
                "latest_game_round": latest_game_round,
                "trump_suit": TRUMP_SUIT_TO_EMOJI[latest_game_round.trump_suit],
                "dealer_name": game_players.get(
                    player_number=dealer_player_number
                ).unique_display_name,
                "game_rounds": game_rounds,
            },
        )


class GameRoundPredictionView(LoginRequiredMixin, FormView):
    """This view allows the user to enter the predictions for a game round."""

    template_name = "game_round_bids.html"
    form_class = GameRoundPredictionForm

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        game = get_object_or_404(Game, pk=self.kwargs["game_id"])
        game_round = get_object_or_404(
            GameRound, round_number=self.kwargs["round_number"], game=game
        )

        if not game_round.visible_to(self.request.user):
            return HttpResponseForbidden()

        return super().get(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return self.request.path

    def get_form_kwargs(self) -> Dict:
        kwargs = super().get_form_kwargs()
        game = get_object_or_404(Game, pk=self.kwargs["game_id"])
        game_round = get_object_or_404(
            GameRound, round_number=self.kwargs["round_number"], game=game
        )

        # We want to display the players in the order they should bid.
        round_players = list(
            GamePlayerGameRound.objects.select_related("game_round", "game_player")
            .filter(game_round=game_round)
            .order_by("game_player__player_number")
            .all()
        )

        # TODO: This is duplicating logic from determining the dealer.
        starting_player_idx = game_round.round_number % len(round_players) + 1

        round_players = (
            round_players[starting_player_idx:] + round_players[:starting_player_idx]
        )

        kwargs["round_players"] = round_players
        kwargs["card_number"] = game_round.card_number

        return kwargs

    def get_context_data(self, **kwargs) -> Dict:
        context = super(GameRoundPredictionView, self).get_context_data(**kwargs)

        game = get_object_or_404(Game, id=self.kwargs["game_id"])
        game_round = get_object_or_404(
            GameRound, round_number=self.kwargs["round_number"], game=game
        )
        game_players = (
            GamePlayer.objects.select_related("game", "player").filter(game=game).all()
        )
        max_score = game_players.aggregate(Max("score"))["score__max"]
        latest_game_round = (
            GameRound.objects.filter(game=game).order_by("round_number").last()
        )
        round_players = list(
            GamePlayerGameRound.objects.select_related("game_round", "game_player")
            .filter(game_round=latest_game_round)
            .order_by("game_player__player_number")
            .all()
        )

        starting_player_idx = game_round.round_number % len(game_players) + 1

        round_players = (
            round_players[starting_player_idx:] + round_players[:starting_player_idx]
        )

        dealer_player_number = latest_game_round.round_number % len(game_players) + 1

        context["game"] = game
        context["game_players"] = game_players
        context["game_player_names"] = ", ".join(
            game_players.values_list("unique_display_name", flat=True)
        )
        context["winning_players"] = ", ".join(
            game_players.filter(score=max_score).values_list(
                "unique_display_name", flat=True
            )
        )
        context["latest_game_round"] = latest_game_round
        context["game_round"] = game_round
        context["trump_suit"] = TRUMP_SUIT_TO_EMOJI[latest_game_round.trump_suit]
        context["dealer_name"] = game_players.get(
            player_number=dealer_player_number
        ).unique_display_name
        context["round_players"] = round_players
        context["player_number"] = (
            self.kwargs.get("player_number")
            or round_players[0].game_player.player_number
        )

        return context

    def form_valid(self, form: GameRoundPredictionForm) -> HttpResponse:
        with transaction.atomic():
            game = get_object_or_404(Game, pk=self.kwargs["game_id"])
            game_round = get_object_or_404(
                GameRound, round_number=self.kwargs["round_number"], game=game
            )

            for round_player in form.cleaned_data:
                player_number = round_player.split("_")[-1]
                tricks_predicted = form.cleaned_data[round_player]
                game_round_game_player = GamePlayerGameRound.objects.get(
                    game_round=game_round, game_player__player_number=player_number
                )

                if game_round_game_player.tricks_won is not None:
                    # We're editing a round which has already completed, so we need to
                    # make sure we don't double-count the score from when this round was
                    # originally played.
                    if (
                        game_round_game_player.tricks_predicted
                        == game_round_game_player.tricks_won
                    ):
                        game_round_game_player.game_player.score -= (
                            game_round.game.correct_prediction_points
                        )

                    if tricks_predicted == game_round_game_player.tricks_won:
                        game_round_game_player.game_player.score += (
                            game_round.game.correct_prediction_points
                        )

                game_round_game_player.tricks_predicted = tricks_predicted
                game_round_game_player.save()
                game_round_game_player.game_player.save()

            total_tricks_predicted = sum(
                round_player.tricks_predicted
                for round_player in game_round.gameplayergameround_set.all()
            )
            game_round.total_tricks_predicted = total_tricks_predicted
            game_round.save()

        return HttpResponseRedirect(f"/games/{game_round.game.id}")


class GameRoundScoreView(LoginRequiredMixin, FormView):
    """This view allows the user to enter the scores for a game round."""

    template_name = "game_round_scores.html"
    form_class = GameRoundScoreForm

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        game = get_object_or_404(Game, pk=self.kwargs["game_id"])
        game_round = get_object_or_404(
            GameRound, round_number=self.kwargs["round_number"], game=game
        )

        if not game_round.visible_to(self.request.user):
            return HttpResponseForbidden()

        return super().get(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return self.request.path

    def get_form_kwargs(self) -> Dict:
        kwargs = super().get_form_kwargs()
        game = get_object_or_404(Game, pk=self.kwargs["game_id"])
        game_round = get_object_or_404(
            GameRound, round_number=self.kwargs["round_number"], game=game
        )

        round_players = list(
            GamePlayerGameRound.objects.select_related("game_round", "game_player")
            .filter(game_round=game_round)
            .order_by("game_player__player_number")
            .all()
        )

        starting_player_idx = game_round.round_number % len(round_players) + 1

        round_players = (
            round_players[starting_player_idx:] + round_players[:starting_player_idx]
        )

        kwargs["round_players"] = round_players
        kwargs["card_number"] = game_round.card_number

        return kwargs

    def get_context_data(self, **kwargs) -> Dict:
        context = super(GameRoundScoreView, self).get_context_data(**kwargs)

        game = get_object_or_404(Game, id=self.kwargs["game_id"])
        game_round = get_object_or_404(
            GameRound, round_number=self.kwargs["round_number"], game=game
        )

        game_players = (
            GamePlayer.objects.select_related("game", "player").filter(game=game).all()
        )
        max_score = game_players.aggregate(Max("score"))["score__max"]
        latest_game_round = (
            GameRound.objects.filter(game=game).order_by("round_number").last()
        )
        round_players = list(
            GamePlayerGameRound.objects.select_related("game_round", "game_player")
            .filter(game_round=game_round)
            .order_by("game_player__player_number")
            .all()
        )

        starting_player_idx = game_round.round_number % len(game_players) + 1

        round_players = (
            round_players[starting_player_idx:] + round_players[:starting_player_idx]
        )

        dealer_player_number = latest_game_round.round_number % len(game_players) + 1

        context["game"] = game
        context["game_players"] = game_players
        context["game_player_names"] = ", ".join(
            game_players.values_list("unique_display_name", flat=True)
        )
        context["winning_players"] = ", ".join(
            game_players.filter(score=max_score).values_list(
                "unique_display_name", flat=True
            )
        )
        context["latest_game_round"] = latest_game_round
        context["game_round"] = game_round
        context["trump_suit"] = TRUMP_SUIT_TO_EMOJI[latest_game_round.trump_suit]
        context["dealer_name"] = game_players.get(
            player_number=dealer_player_number
        ).unique_display_name
        context["round_players"] = round_players
        context["player_number"] = (
            self.kwargs.get("player_number")
            or round_players[0].game_player.player_number
        )

        return context

    def form_valid(self, form: GameRoundScoreForm) -> HttpResponse:
        with transaction.atomic():
            game = get_object_or_404(Game, pk=self.kwargs["game_id"])
            game_round = get_object_or_404(
                GameRound, round_number=self.kwargs["round_number"], game=game
            )

            # TODO: Neaten this up.
            editing_existing_round = False

            for round_player in form.cleaned_data:
                player_number = round_player.split("_")[-1]
                tricks_won = form.cleaned_data[round_player]
                (
                    game_round_game_player,
                    _,
                ) = GamePlayerGameRound.objects.get_or_create(
                    game_round=game_round,
                    game_player__player_number=player_number,
                    defaults={"tricks_won": tricks_won},
                )

                if game_round_game_player.tricks_won is not None:
                    editing_existing_round = True

                if editing_existing_round:
                    old_tricks_won = game_round_game_player.tricks_won

                    game_round_game_player.game_player.score -= old_tricks_won

                    if game_round_game_player.tricks_predicted == old_tricks_won:
                        game_round_game_player.game_player.score -= (
                            game_round.game.correct_prediction_points
                        )

                game_round_game_player.tricks_won = tricks_won

                game_round_game_player.game_player.score += tricks_won

                if (
                    game_round_game_player.tricks_predicted
                    == game_round_game_player.tricks_won
                ):
                    game_round_game_player.game_player.score += (
                        game_round.game.correct_prediction_points
                    )

                game_round_game_player.save()
                game_round_game_player.game_player.save()

            if not editing_existing_round:
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

                # We create the next round of the game, with the next trump suit and the
                # new card number.
                next_round = GameRound.objects.create(
                    game=game_round.game,
                    round_number=game_round.round_number + 1,
                    trump_suit=NEXT_TRUMP_SUIT[game_round.trump_suit],
                    card_number=next_round_card_number,
                )

                # Now set the game_players of the new game_round to the game_players we created
                # earlier. This will also create the GamePlayerGameRound objects.
                next_round.game_players.set(game_round.game_players.all())

                next_round.save()

        return HttpResponseRedirect(f"/games/{game_round.game.id}")
