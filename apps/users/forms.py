from django.contrib.auth.forms import UserChangeForm

from django_registration.forms import RegistrationForm

from .models import User


class UserCreateForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")


class UserUpdateForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Update fields
        self.fields["email"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
