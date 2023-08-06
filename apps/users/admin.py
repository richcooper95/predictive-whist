from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserCreateForm, UserUpdateForm
from .models import User


class UserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name")
    ordering = ("email",)

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "inserted_at", "updated_at")}),
    )

    add_form = UserCreateForm
    form = UserUpdateForm

    readonly_fields = (
        "last_login",
        "inserted_at",
        "updated_at",
    )


admin.site.register(User, UserAdmin)
