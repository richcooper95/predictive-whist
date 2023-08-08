from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.views.generic.edit import UpdateView

from django_registration.backends.one_step.views import RegistrationView  # type: ignore

from apps.games.models import Player
from apps.users.forms import UserUpdateForm


class UserCreateView(RegistrationView):
    """User create view, customised to automatically create a new Player for the user."""

    def register(self, form):
        """
        Register the new user account and immediately log it in.

        """
        new_user = super().register(form)

        # Create a new Player for the user.
        Player.objects.create(
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            created_by_user=new_user,
            user=new_user,
        )

        return new_user


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """User update view."""

    form_class = UserUpdateForm
    template_name = "user_update.html"
    success_url = "/"

    def get_object(self, queryset=None):
        """Get the current user."""
        return self.request.user

    def form_valid(self, form):
        with transaction.atomic():
            # Save the user.
            user = form.save()

            # Update the user's Player's first and last names.
            player = Player.objects.get(user=user)
            player.first_name = user.first_name
            player.last_name = user.last_name
            player.save()

        return super().form_valid(form)
