from django import forms

from apps.games.models import Game

class NewGameForm(forms.ModelForm):
    class Meta:
        model = Game
        exclude = ["is_ongoing", "inserted_at", "updated_at"]
