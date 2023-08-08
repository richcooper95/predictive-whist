from django.contrib.auth.forms import UserChangeForm
from django.forms import ModelForm

from django_registration.forms import RegistrationForm  # type: ignore

from .models import User


class UserCreateForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Update fields
        self.fields["email"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
