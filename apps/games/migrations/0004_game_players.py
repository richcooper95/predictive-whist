# Generated by Django 4.2.3 on 2023-07-26 15:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0003_rename_created_by_user_id_player_created_by_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="players",
            field=models.ManyToManyField(through="games.GamePlayer", to="games.player"),
        ),
    ]