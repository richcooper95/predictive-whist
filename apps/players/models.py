from typing import Any, List
from django.db import models
from django.conf import settings

from hashid_field import BigHashidAutoField  # type: ignore


class Player(models.Model):
    """A player.

    Attributes:
        first_name (str): The first name of the player.
        last_name (str): The last name of the player.
        user (str): The user represented by this player.
        created_by_user (auth.User): The user who created this player.
        inserted_at (datetime): The datetime when this player was created.
        updated_at (datetime): The datetime when this player was last updated.
    """

    id = BigHashidAutoField(primary_key=True, prefix="pla_")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_players",
    )
    is_deleted = models.BooleanField(default=False)

    inserted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def delete(self, using=None, keep_parents=False) -> Any:
        """Soft-deletes this player so they still appear in historic games."""
        self.is_deleted = True
        self.save()

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

    def unique_display_name(self, players: List["Player"]) -> str:
        """Returns a unique display name for this player within the given list of players.

        This one of the following, in order of preference:
        - The player's first name, if that is unique.
        - The player's first name and however many letters of the surname are required to
          make it unique.
        - The player's first name (as a fallback). This will not be unique.

        Args:
            players (List[Player]): The list of all players in a game.

        Returns:
            str: The unique player name.
        """
        if len([p for p in players if self.first_name == p.first_name]) == 1:
            return self.first_name

        # There is more than one player with this first name. Append as many letters as
        # necessary from the surname to make it unique.
        for i in range(1, len(self.last_name) - 1):
            truncated_last_name = f"{self.last_name[:i]}"
            if (
                len(
                    [
                        p
                        for p in players
                        if p.first_name == self.first_name
                        and p.last_name.startswith(truncated_last_name)
                    ]
                )
                == 1
            ):
                return self.first_name + " " + truncated_last_name + "."

        return self.full_name()

    def initials(self) -> str:
        """The initials of this player.

        Returns:
            str: The initials of this player.
        """

        def _initials(string) -> str:
            return "".join(s[0] for s in string.replace(" ", "-").split("-"))

        return _initials(self.first_name) + _initials(self.last_name)
