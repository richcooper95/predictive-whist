from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Home view."""

    template_name = "index.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, {})


class InfoView(TemplateView):
    """Info view."""

    template_name = "info.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, {})


class RulesView(TemplateView):
    """Rules view."""

    template_name = "rules.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, {})


class PrivacyPolicyView(TemplateView):
    """Privacy policy view."""

    template_name = "privacy.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, {})
