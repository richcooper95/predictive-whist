import datetime
import random
from typing import Dict, List
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import Game, Player


class GameModelForm(forms.ModelForm):
    """Form for creating a new game.

    This form is used in the GameCreateView.
    """

    # TODO: Enable users to choose the player order in the form.
    players = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user", None)
        initial = kwargs.pop("initial", {})

        if initial.get("name") is None:
            initial["name"] = self.create_name_suggestion()

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        # TODO: Enable users to choose the player order in the form.
        # TODO: See if we can find a way to define this without type: ignore.
        self.fields["players"].queryset = (  # type: ignore[attr-defined]
            Player.objects.filter(created_by_user=self.user)
            .exclude(is_deleted=True)
            .all()
        )

    class Meta:
        model = Game
        fields = (
            "name",
            "players",
            "starting_round_card_number",
            "number_of_decks",
            "correct_prediction_points",
        )
        help_texts = {
            "name": "What do you want to name your game?",
            "starting_round_card_number": "How many cards should be dealt in the first round?",
            "number_of_decks": "How many decks of cards are in play?",
            "correct_prediction_points": (
                "How many points should be awarded for a correct prediction?"
            ),
        }
        labels = {
            "name": "Name",
            "players": "Players",
            "starting_round_card_number": "Starting Card Number",
            "number_of_decks": "Number of Decks",
            "correct_prediction_points": "Correct Prediction Points",
        }

    def create_name_suggestion(self) -> str:
        """Create a name suggestion for the game.

        Returns:
            str: A name suggestion for the game.
        """
        adjectives = [
            "Big",
            "Huge",
            "Fun",
            "Epic",
            "Amazing",
            "Cool",
            "Awesome",
            "Tricky",
            "Crazy",
            "Wild",
        ]

        nouns = [
            "Game",
            "Championship",
            "Competition",
            "Showdown",
            "Match",
        ]

        year = datetime.datetime.strftime(datetime.datetime.now(), "%y")

        return f"The {random.choice(adjectives)} Whist {random.choice(nouns)} '{year}"

    def clean_players(self) -> List[Player]:
        """Validate the players field.

        Raises:
            forms.ValidationError: If less than two players are selected.

        Returns:
            List[Player]: The cleaned players.
        """
        players = self.cleaned_data["players"]

        if len(players) < 2:
            raise forms.ValidationError(
                "You must select at least two players to start a game."
            )

        return players

    def clean_number_of_decks(self) -> int:
        """Validate the number of decks field.

        Raises:
            forms.ValidationError: If the number of decks is less than 1.

        Returns:
            int: The cleaned number of decks.
        """
        number_of_decks = self.cleaned_data["number_of_decks"]

        if number_of_decks < 1:
            raise forms.ValidationError(
                "You must select at least one deck to start a game."
            )

        return number_of_decks

    def clean_correct_prediction_points(self) -> int:
        """Validate the correct prediction points field.

        Raises:
            forms.ValidationError: If the correct prediction points are less than 0.

        Returns:
            int: The cleaned correct prediction points.
        """
        correct_prediction_points = self.cleaned_data["correct_prediction_points"]

        if correct_prediction_points < 0:
            raise forms.ValidationError(
                "The correct prediction points must be greater than or equal to 0."
            )

        return correct_prediction_points

    def clean(self) -> Dict:
        """Validate the form as a whole.

        This method is called after the individual field validators are called.

        Raises:
            forms.ValidationError: If the starting round card number is not between 1 and
                the maximum possible starting round card number.

        Returns:
            Dict: The cleaned data.
        """
        cleaned_data = super().clean()

        assert cleaned_data is not None

        players = cleaned_data["players"]
        starting_round_card_number = cleaned_data["starting_round_card_number"]
        number_of_decks = cleaned_data["number_of_decks"]

        max_starting_round_card_number = (number_of_decks * 52) // len(players)

        if (
            starting_round_card_number < 1
            or starting_round_card_number > max_starting_round_card_number
        ):
            raise forms.ValidationError(
                "The starting round card number must be between 1 and "
                f"{max_starting_round_card_number} with {len(players)} players.",
            )

        return cleaned_data


class PlayerModelForm(forms.ModelForm):
    """Form for creating a new player."""

    class Meta:
        model = Player
        fields = (
            "first_name",
            "last_name",
        )


class GameRoundPredictionForm(forms.Form):
    """Form for predicting the number of tricks each player will win in a round."""

    def __init__(self, *args, **kwargs) -> None:
        self.card_number = kwargs.pop("card_number")

        round_players = kwargs.pop("round_players")

        super().__init__(*args, **kwargs)

        # Add a field to contain the prediction of each player in the round. The field
        # name is dynamically generated based on the player number. The field is
        # initialised with the number of tricks predicted by the player in the round, to
        # allow the user to edit their prediction.
        for round_player in round_players:
            field_name = f"tricks_predicted_{round_player.game_player.player_number}"
            self.fields[field_name] = forms.IntegerField(
                required=True,
                initial=round_player.tricks_predicted,
                validators=[MaxValueValidator(self.card_number), MinValueValidator(0)],
            )

    def clean(self) -> Dict:
        """Validate the form as a whole.

        This method is called after the individual field validators are called.

        Raises:
            forms.ValidationError: If the total number of tricks predicted is equal to
                the number of cards in the round.

        Returns:
            Dict: The cleaned data.
        """
        cleaned_data = super().clean()

        assert cleaned_data is not None

        if sum(cleaned_data.values()) == self.card_number:
            raise forms.ValidationError(
                "The total number of tricks predicted must not be equal to "
                f"{self.card_number}. The dealer must choose a different bid."
            )

        return cleaned_data


class GameRoundScoreForm(forms.Form):
    """Form for scoring the number of tricks each player has won in a round."""

    def __init__(self, *args, **kwargs) -> None:
        self.card_number = kwargs.pop("card_number")

        round_players = kwargs.pop("round_players")

        super().__init__(*args, **kwargs)

        for round_player in round_players:
            field_name = f"tricks_won_{round_player.game_player.player_number}"
            self.fields[field_name] = forms.IntegerField(
                required=True,
                initial=round_player.tricks_won,
                validators=[MaxValueValidator(self.card_number), MinValueValidator(0)],
            )

    def clean(self) -> Dict:
        """Validate the form as a whole.

        This method is called after the individual field validators are called.

        Raises:
            forms.ValidationError: If the total number of tricks scored is not equal to
                the number of cards in the round.

        Returns:
            Dict: The cleaned data.
        """
        cleaned_data = super().clean()

        assert cleaned_data is not None

        if sum(cleaned_data.values()) != self.card_number:
            raise forms.ValidationError(
                f"The total number of tricks scored must be equal to {self.card_number}."
            )

        return cleaned_data
