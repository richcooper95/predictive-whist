from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from ..models import User


class UserTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="somethingelse@example.com",
            first_name="First",
            last_name="Last",
            password="S0me-password",
        )

        self.assertEqual(user.email, "somethingelse@example.com")
        self.assertEqual(user.first_name, "First")
        self.assertEqual(user.last_name, "Last")
        self.assertTrue(user.check_password("S0me-password"))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            _ = User.objects.create_user(
                email="",
                first_name="First",
                last_name="Last",
                password="S0me-password",
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="somethingelse@example.com",
            first_name="First",
            last_name="Last",
            password="S0me-password",
        )

        self.assertEqual(user.email, "somethingelse@example.com")
        self.assertEqual(user.first_name, "First")
        self.assertEqual(user.last_name, "Last")
        self.assertTrue(user.check_password("S0me-password"))
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

    def test_create_superuser_without_email(self):
        with self.assertRaises(ValueError):
            _ = User.objects.create_superuser(
                email="",
                first_name="First",
                last_name="Last",
                password="S0me-password",
            )

    def test_create_superuser_without_is_staff(self):
        with self.assertRaises(ValueError):
            _ = User.objects.create_superuser(
                email="something@example.com",
                first_name="First",
                last_name="Last",
                password="S0me-password",
                is_staff=False,
            )

    def test_create_superuser_without_is_superuser_raises_error(self):
        with self.assertRaises(ValueError):
            _ = User.objects.create_superuser(
                email="something@example.com",
                first_name="First",
                last_name="Last",
                password="S0me-password",
                is_superuser=False,
            )

    def test_email_is_unique(self):
        User.objects.create_user(
            email="something@example.com",
            first_name="First",
            last_name="Last",
            password="S0me-password",
        )

        with self.assertRaises(ValidationError) as context:
            User(
                email="something@example.com",
                first_name="Another",
                last_name="Name",
                password="S0me-other-password",
            ).full_clean()

        self.assertIn("email", context.exception.error_dict)


class UserUnitTest(SimpleTestCase):
    def setUp(self):
        self.user = User(
            email="something@example.com",
            first_name="First",
            last_name="Last",
            password="S0me-password",
        )

    def test_str(self):
        self.assertEqual(str(self.user), "something@example.com")

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), "First Last")

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), "First")

    def test_clean_lowercases_email_domain(self):
        user = User(
            email="somethingelse@eXaMpLe.com",
            first_name="First",
            last_name="Last",
            password="S0me-password",
        )

        user.clean()

        self.assertEqual(user.email, "somethingelse@example.com")

    def test_clean_does_not_lowercase_email_local_part(self):
        user = User(
            email="SoMeThInG@example.com",
            first_name="First",
            last_name="Last",
            password="S0me-password",
        )

        user.clean()

        self.assertEqual(user.email, "SoMeThInG@example.com")

    def test_required_fields(self):
        with self.assertRaises(ValidationError) as context:
            User().clean_fields()

        self.assertIn("first_name", context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict["first_name"][0].message,
            "This field cannot be blank.",
        )

        self.assertIn("last_name", context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict["last_name"][0].message,
            "This field cannot be blank.",
        )

        self.assertIn("email", context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict["email"][0].message,
            "This field cannot be blank.",
        )

    def test_email_validation(self):
        with self.assertRaises(ValidationError) as context:
            User(email="something").clean_fields()

        self.assertIn("email", context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict["email"][0].message,
            "Enter a valid email address.",
        )

    def test_email_max_length(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Ensure this value has at most 255 characters (it has 256).",
        ) as context:
            User(email="a" * 244 + "@example.com").clean_fields()

        self.assertIn("email", context.exception.error_dict)

    def test_first_name_max_length(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Ensure this value has at most 150 characters (it has 151).",
        ) as context:
            User(first_name="a" * 151).clean_fields()

        self.assertIn("first_name", context.exception.error_dict)

    def test_last_name_max_length(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Ensure this value has at most 150 characters (it has 151).",
        ) as context:
            User(last_name="a" * 151).clean_fields()

        self.assertIn("last_name", context.exception.error_dict)
