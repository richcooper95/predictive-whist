from django.db import models
from django.conf import settings

from hashid_field import BigHashidAutoField


class Player(models.Model):
    """A player.

    Attributes:
        first_name (str): The first name of the player.
        last_name (str): The last name of the player.
        created_by_user (auth.User): The user who created this player.
        inserted_at (datetime): The datetime when this player was created.
        updated_at (datetime): The datetime when this player was last updated.
    """

    id = BigHashidAutoField(primary_key=True, prefix="pla_")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def visible_to(self, user) -> bool:
        """Whether the given user can see this player.

        Args:
            user (auth.User): The user to check.

        Returns:
            bool: Whether the given user can see this player.
        """
        return self.created_by_user == user or user.is_superuser

    def full_name(self) -> str:
        """The full name of this player.

        Returns:
            str: The full name of this player.
        """
        return self.first_name + " " + self.last_name


class Game(models.Model):
    """A game.

    Attributes:
        name (str): The name of the game.
        is_ongoing (bool): Whether the game is ongoing.
        correct_prediction_points (int):
            The number of points awarded for a correct prediction of the number of tricks
            a player will win.
        starting_round_card_number (int):
            The number of cards dealt to each player in the first round.
        card_number_descending (bool):
            Whether the number of cards dealt to each player should decrease by one in
            the next round.
        number_of_decks (int): The number of decks of cards in play.
        created_by_user (auth.User): The user who created this game.
        players (list of Player): The players in this game.
        inserted_at (datetime): The datetime when this game was created.
        updated_at (datetime): The datetime when this game was last updated.
    """

    id = BigHashidAutoField(primary_key=True, prefix="gam_")
    name = models.CharField(max_length=255)
    is_ongoing = models.BooleanField(default=True)
    correct_prediction_points = models.IntegerField(default=5)
    starting_round_card_number = models.IntegerField()
    card_number_descending = models.BooleanField(default=True)
    number_of_decks = models.IntegerField(default=1)

    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    players = models.ManyToManyField(Player, through="GamePlayer")

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    def visible_to(self, user) -> bool:
        """Whether the given user can see this game.

        Args:
            user (auth.User): The user to check.

        Returns:
            bool: Whether the given user can see this game.
        """
        return self.created_by_user == user or user.is_superuser


class GamePlayer(models.Model):
    """A player in a game.

    This is a through model for the many-to-many relationship between Game and Player.

    Attributes:
        game (Game): The game.
        player (Player): The player.
        player_number (int): The number of the player in the game.
        score (int): The score of the player in the game.
        inserted_at (datetime): The datetime when this player was added to the game.
        updated_at (datetime): The datetime when this game player was last updated.
        unique_display_name (str): The unique display name of this game player.
    """

    id = BigHashidAutoField(primary_key=True, prefix="gpl_")
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    player_number = models.IntegerField()
    score = models.IntegerField(default=0)
    unique_display_name = models.CharField(max_length=255, blank=True, null=True)

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["player_number"]

    def __str__(self) -> str:
        return str(self.game_id) + " - " + str(self.player_id)

    def visible_to(self, user) -> bool:
        """Whether the given user can see this game player.

        Args:
            user (auth.User): The user to check.

        Returns:
            bool: Whether the given user can see this game player.
        """
        return self.game.visible_to(user)


class GameRound(models.Model):
    """A round in a game.

    Attributes:
        game (Game): The game.
        round_number (int): The number of the round in the game.
        trump_suit (str): The suit of the trump card.
        card_number (int): The number of cards dealt to each player in this round.
        total_tricks_predicted (int): The total number of tricks predicted by all players.
        game_players (list of GamePlayer): The game players in this round.
        inserted_at (datetime): The datetime when this round was created.
        updated_at (datetime): The datetime when this round was last updated.
    """

    id = BigHashidAutoField(primary_key=True, prefix="rou_")
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
    game_players = models.ManyToManyField(GamePlayer, through="GamePlayerGameRound")

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def visible_to(self, user) -> bool:
        """Whether the given user can see this game round.

        Args:
            user (auth.User): The user to check.

        Returns:
            bool: Whether the given user can see this game round.
        """
        return self.game.visible_to(user)


class GamePlayerGameRound(models.Model):
    """A game player in a round.

    This is a through model for the many-to-many relationship between GameRound and
    GamePlayer.

    Attributes:
        game_round (GameRound): The game round.
        game_player (GamePlayer): The game player.
        tricks_predicted (int):
            The number of tricks predicted by the game player in the game round.
        tricks_won (int):
            The number of tricks won by the game player in the game round.
        inserted_at (datetime):
            The datetime when this game player game round was added to the game.
        updated_at (datetime):
            The datetime when this game player game round was last updated.
    """

    id = BigHashidAutoField(primary_key=True, prefix="rgp_")
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE)
    game_player = models.ForeignKey(GamePlayer, on_delete=models.CASCADE)
    tricks_predicted = models.IntegerField(null=True)
    tricks_won = models.IntegerField(null=True)

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.game_round_id) + " - " + str(self.game_player_id)

    def visible_to(self, user) -> bool:
        """Whether the given user can see this game player game round.

        Args:
            user (auth.User): The user to check.

        Returns:
            bool: Whether the given user can see this game player game round.
        """
        return self.game_round.game.visible_to(user)
