from django_registration.backends.one_step.views import RegistrationView

from apps.games.models import Player


# Create your views here.
class UserCreateView(RegistrationView):
    """User create view, customised to automatically create a new Player for the user."""

    def register(self, form):
        """
        Register the new user account and immediately log it in.

        """
        new_user = super().register(form)

        # Create a new Player for the user
        Player.objects.create(
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            created_by_user=new_user,
        )

        return new_user
