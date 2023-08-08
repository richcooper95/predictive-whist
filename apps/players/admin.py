from django.contrib import admin

from .models import Player


class PlayerAdmin(admin.ModelAdmin):
    readonly_fields = ("inserted_at", "updated_at")

admin.site.register(Player, PlayerAdmin)
