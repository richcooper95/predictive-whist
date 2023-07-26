# Generated by Django 4.2.3 on 2023-07-19 13:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("is_ongoing", models.BooleanField(default=True)),
                ("correct_prediction_points", models.IntegerField(default=5)),
                ("vary_round_card_number", models.BooleanField(default=True)),
                ("starting_round_card_number", models.IntegerField()),
                ("total_card_number", models.IntegerField(default=52)),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="GamePlayer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("player_number", models.IntegerField()),
                ("score", models.IntegerField(default=0)),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "game_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="games.game"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GameRound",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("round_number", models.IntegerField(default=1)),
                (
                    "trump_suit",
                    models.CharField(
                        choices=[
                            ("H", "Hearts"),
                            ("S", "Spades"),
                            ("D", "Diamonds"),
                            ("C", "Clubs"),
                            ("N", "No Trumps"),
                        ],
                        default="H",
                        max_length=1,
                    ),
                ),
                ("card_number", models.IntegerField()),
                ("total_tricks_predicted", models.IntegerField()),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "game_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="games.game"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by_user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GameRoundPlayer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tricks_predicted", models.IntegerField()),
                ("tricks_won", models.IntegerField()),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "game_player_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="games.gameplayer",
                    ),
                ),
                (
                    "game_round_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="games.gameround",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="gameplayer",
            name="player_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="games.player"
            ),
        ),
    ]