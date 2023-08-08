from django import forms

from .models import Player


class PlayerModelForm(forms.ModelForm):
    """Form for creating a new player."""

    class Meta:
        model = Player
        fields = (
            "first_name",
            "last_name",
        )
