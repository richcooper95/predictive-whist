from django.test import TestCase
from django.urls import reverse


class HomeViewTest(TestCase):
    def test_get_by_path(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "index.html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h4>Welcome to 🃏 What's Trumps?</h4>")

    def test_get_by_name(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "index.html")
        self.assertEqual(response.status_code, 200)

    def test_only_get_method_allowed(self):
        response = self.client.put("/")
        self.assertEqual(response.status_code, 405)

        response = self.client.delete("/")
        self.assertEqual(response.status_code, 405)

        response = self.client.patch("/")
        self.assertEqual(response.status_code, 405)


class InfoViewTest(TestCase):
    def test_get_by_path(self):
        response = self.client.get("/info/")
        self.assertTemplateUsed(response, "info.html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h4>What's What's Trumps?</h4>")

    def test_get_by_name(self):
        response = self.client.get(reverse("info"))
        self.assertTemplateUsed(response, "info.html")
        self.assertEqual(response.status_code, 200)

    def test_only_get_method_allowed(self):
        response = self.client.put("/info/")
        self.assertEqual(response.status_code, 405)

        response = self.client.delete("/info/")
        self.assertEqual(response.status_code, 405)

        response = self.client.patch("/info/")
        self.assertEqual(response.status_code, 405)


class RulesViewTest(TestCase):
    def test_get_by_path(self):
        response = self.client.get("/rules/")
        self.assertTemplateUsed(response, "rules.html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h5>👨‍👩‍👧‍👦 Players and Cards</h5>")

    def test_get_by_name(self):
        response = self.client.get(reverse("rules"))
        self.assertTemplateUsed(response, "rules.html")
        self.assertEqual(response.status_code, 200)

    def test_only_get_method_allowed(self):
        response = self.client.put("/rules/")
        self.assertEqual(response.status_code, 405)

        response = self.client.delete("/rules/")
        self.assertEqual(response.status_code, 405)

        response = self.client.patch("/rules/")
        self.assertEqual(response.status_code, 405)
