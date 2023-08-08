# Generated by Django 4.2.3 on 2023-08-08 19:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("games", "0002_initial"),
        ("players", "0001_initial"),
    ]

    operations = [
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
            field=models.ManyToManyField(
                through="games.GamePlayer", to="players.player"
            ),
        ),
    ]
