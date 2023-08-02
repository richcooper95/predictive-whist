from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.games.models import Game, Player


class GameModelForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(GameModelForm, self).__init__(*args, **kwargs)

        self.fields["players"].queryset = Player.objects.filter(
            created_by_user=self.user
        ).all()

    class Meta:
        model = Game
        exclude = [
            "is_ongoing",
            "card_number_descending",
            "created_by_user",
            "inserted_at",
            "updated_at",
        ]

    def clean_players(self):
        players = self.cleaned_data["players"]

        if len(players) < 2:
            raise forms.ValidationError(
                "You must select at least two players to start a game."
            )

        return players

    def clean_number_of_decks(self):
        number_of_decks = self.cleaned_data["number_of_decks"]

        if number_of_decks < 1:
            raise forms.ValidationError(
                "You must select at least one deck to start a game."
            )

        return number_of_decks

    def clean_correct_prediction_points(self):
        correct_prediction_points = self.cleaned_data["correct_prediction_points"]

        if correct_prediction_points < 0:
            raise forms.ValidationError(
                "The correct prediction points must be greater than or equal to 0."
            )

        return correct_prediction_points

    def clean(self):
        cleaned_data = super().clean()

        players = cleaned_data.get("players")
        starting_round_card_number = cleaned_data.get("starting_round_card_number")
        number_of_decks = cleaned_data.get("number_of_decks")

        if all(
            x is not None
            for x in [players, starting_round_card_number, number_of_decks]
        ):
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
    class Meta:
        model = Player
        exclude = ["created_by_user", "inserted_at", "updated_at"]


class GameRoundPredictionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.card_number = kwargs.pop("card_number")

        round_players = kwargs.pop("round_players")

        super().__init__(*args, **kwargs)

        for round_player in round_players:
            field_name = f"tricks_predicted_{round_player.game_player.player_number}"
            self.fields[field_name] = forms.IntegerField(
                required=True,
                initial=round_player.tricks_predicted,
                validators=[MaxValueValidator(self.card_number), MinValueValidator(0)],
            )

    def clean(self):
        cleaned_data = super().clean()

        if sum(cleaned_data.values()) == self.card_number:
            raise forms.ValidationError(
                "The total number of tricks predicted must not be equal to "
                f"{self.card_number}. The dealer must choose a different bid."
            )

        if any(x > self.card_number for x in cleaned_data.values()):
            raise forms.ValidationError(
                f"No individual bid can be greater than {self.card_number}."
            )

        if any(x < 0 for x in cleaned_data.values()):
            raise forms.ValidationError(f"No bid can be less than 0.")

        return cleaned_data


class GameRoundScoreForm(forms.Form):
    def __init__(self, *args, **kwargs):
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

    def clean(self):
        cleaned_data = super().clean()

        if sum(cleaned_data.values()) != self.card_number:
            raise forms.ValidationError(
                f"The total number of tricks scored must be equal to {self.card_number}."
            )

        if any(x > self.card_number for x in cleaned_data.values()):
            raise forms.ValidationError(
                f"No individual score can be greater than {self.card_number}."
            )

        if any(x < 0 for x in cleaned_data.values()):
            raise forms.ValidationError(f"No score can be less than 0.")

        return cleaned_data
