from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Login")
        return context


class CustomLogoutView(LogoutView):
    next_page = "/"


class ProfileView(DetailView):
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile_user"

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs["username"])
