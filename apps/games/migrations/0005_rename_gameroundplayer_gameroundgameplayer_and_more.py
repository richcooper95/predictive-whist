# Generated by Django 4.2.3 on 2023-07-26 17:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0004_game_players"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="GameRoundPlayer",
            new_name="GameRoundGamePlayer",
        ),
        migrations.AlterModelOptions(
            name="gameplayer",
            options={"ordering": ["player_number"]},
        ),
        migrations.RemoveField(
            model_name="game",
            name="total_card_number",
        ),
        migrations.RemoveField(
            model_name="game",
            name="vary_round_card_number",
        ),
        migrations.AddField(
            model_name="game",
            name="number_of_decks",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="gameround",
            name="game_players",
            field=models.ManyToManyField(
                through="games.GameRoundGamePlayer", to="games.gameplayer"
            ),
        ),
    ]