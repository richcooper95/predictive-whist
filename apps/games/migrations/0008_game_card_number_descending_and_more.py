# Generated by Django 4.2.3 on 2023-07-28 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_alter_gameroundgameplayer_tricks_predicted_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='card_number_descending',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='gameround',
            name='round_number',
            field=models.IntegerField(),
        ),
    ]
