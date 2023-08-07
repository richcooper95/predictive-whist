# Generated by Django 4.2.3 on 2023-08-07 12:01

from django.db import migrations, models
import hashid_field.field


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                (
                    "id",
                    hashid_field.field.BigHashidAutoField(
                        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
                        min_length=13,
                        prefix="gam_",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("is_ongoing", models.BooleanField(default=True)),
                ("correct_prediction_points", models.IntegerField(default=5)),
                ("starting_round_card_number", models.IntegerField()),
                ("card_number_descending", models.BooleanField(default=True)),
                ("number_of_decks", models.IntegerField(default=1)),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="GamePlayer",
            fields=[
                (
                    "id",
                    hashid_field.field.BigHashidAutoField(
                        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
                        min_length=13,
                        prefix="gpl_",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("player_number", models.IntegerField()),
                ("score", models.IntegerField(default=0)),
                ("unique_display_name", models.CharField(max_length=255)),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["player_number"],
            },
        ),
        migrations.CreateModel(
            name="GamePlayerGameRound",
            fields=[
                (
                    "id",
                    hashid_field.field.BigHashidAutoField(
                        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
                        min_length=13,
                        prefix="rgp_",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("tricks_predicted", models.IntegerField(null=True)),
                ("tricks_won", models.IntegerField(null=True)),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="GameRound",
            fields=[
                (
                    "id",
                    hashid_field.field.BigHashidAutoField(
                        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
                        min_length=13,
                        prefix="rou_",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("round_number", models.IntegerField()),
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
                ("total_tricks_predicted", models.IntegerField(null=True)),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    hashid_field.field.BigHashidAutoField(
                        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
                        min_length=13,
                        prefix="pla_",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("inserted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
