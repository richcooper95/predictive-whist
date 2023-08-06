from django.contrib import admin

from .models import Player, Game, GamePlayer, GameRound, GamePlayerGameRound


# Register your models here.
class PlayerAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")


class GameAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")


class GamePlayerAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")


class GameRoundAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")


class GamePlayerGameRoundAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")


admin.site.register(Player, PlayerAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(GamePlayer, GamePlayerAdmin)
admin.site.register(GameRound, GameRoundAdmin)
admin.site.register(GamePlayerGameRound, GamePlayerGameRoundAdmin)
