from django.test import TestCase
from django.urls import reverse

from apps.games.models import Player

from ..models import User


class UserCreateViewTest(TestCase):
    def test_get_by_path(self):
        response = self.client.get("/accounts/register/")
        self.assertTemplateUsed(response, "django_registration/registration_form.html")
        self.assertEqual(response.status_code, 200)

    def test_get_by_name(self):
        response = self.client.get(reverse("django_registration_register"))
        self.assertTemplateUsed(response, "django_registration/registration_form.html")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "email": "something@example.com",
                "password1": "S0me-password",
                "password2": "S0me-password",
                "first_name": "First",
                "last_name": "Last",
            },
        )
        self.assertRedirects(response, "/accounts/register/complete/")
        self.assertEqual(response.status_code, 302)

        # Check that the user was created.
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email="something@example.com")
        self.assertEqual(user.first_name, "First")
        self.assertEqual(user.last_name, "Last")

        # Check that the user is logged in.
        self.assertTrue(user.is_authenticated)

        # Check that the user is not a superuser.
        self.assertFalse(user.is_superuser)

        # Check that the player was created.
        self.assertEqual(Player.objects.count(), 1)
        player = Player.objects.get(created_by_user=user)
        self.assertEqual(player.first_name, "First")
        self.assertEqual(player.last_name, "Last")

    def test_only_get_and_post_methods_allowed(self):
        response = self.client.put("/")
        self.assertEqual(response.status_code, 405)

        response = self.client.delete("/")
        self.assertEqual(response.status_code, 405)

        response = self.client.patch("/")
        self.assertEqual(response.status_code, 405)
