from django import forms

from apps.games.models import Game, Player


class GameModelForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(
        queryset=Player.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Game
        exclude = ["is_ongoing", "inserted_at", "updated_at"]

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

        if all(x is not None for x in [players, starting_round_card_number, number_of_decks]):
            max_starting_round_card_number = (number_of_decks * 52) // len(players)

            if starting_round_card_number < 1 or starting_round_card_number > 13:
                raise forms.ValidationError(
                    "The starting round card number must be between 1 and %(max_starting_round_card_number)s with %(player_count)s players.",
                    params={
                        "player_count": len(players),
                        "max_starting_round_card_number": max_starting_round_card_number,
                    },
                )

            return cleaned_data


class PlayerModelForm(forms.ModelForm):
    class Meta:
        model = Player
        exclude = ["created_by_user", "inserted_at", "updated_at"]
