# Generated by Django 4.2.3 on 2023-08-06 22:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("games", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="created_by_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="gameround",
            name="game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="games.game"
            ),
        ),
        migrations.AddField(
            model_name="gameround",
            name="game_players",
            field=models.ManyToManyField(
                through="games.GamePlayerGameRound", to="games.gameplayer"
            ),
        ),
        migrations.AddField(
            model_name="gameplayergameround",
            name="game_player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="games.gameplayer"
            ),
        ),
        migrations.AddField(
            model_name="gameplayergameround",
            name="game_round",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="games.gameround"
            ),
        ),
        migrations.AddField(
            model_name="gameplayer",
            name="game",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="games.game"
            ),
        ),
        migrations.AddField(
            model_name="gameplayer",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="games.player"
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="created_by_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="players",
            field=models.ManyToManyField(through="games.GamePlayer", to="games.player"),
        ),
    ]
