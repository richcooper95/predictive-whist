# Generated by Django 4.2.3 on 2023-07-19 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gameplayer',
            old_name='game_id',
            new_name='game',
        ),
        migrations.RenameField(
            model_name='gameplayer',
            old_name='player_id',
            new_name='player',
        ),
        migrations.RenameField(
            model_name='gameround',
            old_name='game_id',
            new_name='game',
        ),
        migrations.RenameField(
            model_name='gameroundplayer',
            old_name='game_player_id',
            new_name='game_player',
        ),
        migrations.RenameField(
            model_name='gameroundplayer',
            old_name='game_round_id',
            new_name='game_round',
        ),
    ]
