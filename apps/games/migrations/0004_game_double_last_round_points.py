# Generated by Django 4.2.3 on 2023-08-21 22:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0003_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="double_last_round_points",
            field=models.BooleanField(default=False),
        ),
    ]
