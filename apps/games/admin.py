from django.contrib import admin

from .models import Game, GamePlayer, GameRound, GamePlayerGameRound


class GameAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")


class GamePlayerAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")


class GameRoundAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")


class GamePlayerGameRoundAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")


admin.site.register(Game, GameAdmin)
admin.site.register(GamePlayer, GamePlayerAdmin)
admin.site.register(GameRound, GameRoundAdmin)
admin.site.register(GamePlayerGameRound, GamePlayerGameRoundAdmin)
