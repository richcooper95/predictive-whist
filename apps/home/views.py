from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class HomeView(TemplateView):
    """Home view."""

    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
