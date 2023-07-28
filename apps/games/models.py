from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=255)
    created_by_user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def visible_to(self, user):
        return self.created_by_user == user or user.is_superuser


class Game(models.Model):
    name = models.CharField(max_length=255)
    is_ongoing = models.BooleanField(default=True)
    correct_prediction_points = models.IntegerField(default=5)
    starting_round_card_number = models.IntegerField()
    card_number_descending = models.BooleanField(default=True)
    number_of_decks = models.IntegerField(default=1)

    created_by_user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    players = models.ManyToManyField(Player, through="GamePlayer")

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def visible_to(self, user):
        return self.created_by_user == user or user.is_superuser


class GamePlayer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    player_number = models.IntegerField()
    score = models.IntegerField(default=0)

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["player_number"]

    def __str__(self):
        return str(self.game_id) + " - " + str(self.player_id)

    def visible_to(self, user):
        return self.game.visible_to(user)


class GameRound(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    round_number = models.IntegerField()
    trump_suit = models.CharField(
        max_length=1,
        default="H",
        choices=[
            ("H", "Hearts"),
            ("S", "Spades"),
            ("D", "Diamonds"),
            ("C", "Clubs"),
            ("N", "No Trumps"),
        ],
    )
    card_number = models.IntegerField()
    total_tricks_predicted = models.IntegerField(null=True)
    game_players = models.ManyToManyField(GamePlayer, through="GameRoundGamePlayer")

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def visible_to(self, user):
        return self.game.visible_to(user)


class GameRoundGamePlayer(models.Model):
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE)
    game_player = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    tricks_predicted = models.IntegerField(null=True)
    tricks_won = models.IntegerField(null=True)

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.game_round_id) + " - " + str(self.game_player_id)

    def visible_to(self, user):
        return self.game_round.game.visible_to(user)
