# Generated by Django 4.2.3 on 2023-07-28 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0009_game_winning_player'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='winning_player',
        ),
    ]