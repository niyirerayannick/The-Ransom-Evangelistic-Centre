from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import update_session_auth_hash
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from apps.dashboard.forms import DashboardLoginForm, PasswordChangeDashboardForm, ProfileForm
from apps.dashboard.permissions import DashboardAccessMixin


class DashboardLoginView(LoginView):
    template_name = "dashboard/login.html"
    authentication_form = DashboardLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        remember = self.request.POST.get("remember_me")
        if remember:
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            self.request.session.set_expiry(0)
        return self.request.user.get_login_redirect_url()

    def form_valid(self, form):
        ip = self.request.META.get("REMOTE_ADDR", "unknown")
        key = f"dashboard_login_fail_{ip}"
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, _("This account is inactive."))
            return self.form_invalid(form)
        if not user.can_access_dashboard():
            messages.error(self.request, _("You do not have dashboard access."))
            return self.form_invalid(form)
        cache.delete(key)
        messages.success(self.request, _("Welcome back!"))
        return super().form_valid(form)

    def form_invalid(self, form):
        ip = self.request.META.get("REMOTE_ADDR", "unknown")
        key = f"dashboard_login_fail_{ip}"
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, 900)
        if attempts >= 5:
            messages.error(
                self.request,
                _("Too many failed login attempts. Please wait 15 minutes and try again."),
            )
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        ip = request.META.get("REMOTE_ADDR", "unknown")
        key = f"dashboard_login_fail_{ip}"
        if cache.get(key, 0) >= 5 and request.method == "POST":
            messages.error(
                request,
                _("Too many failed login attempts. Please wait 15 minutes and try again."),
            )
            return render(request, self.template_name, {"form": self.get_form()})
        return super().dispatch(request, *args, **kwargs)


class DashboardLogoutView(LogoutView):
    next_page = reverse_lazy("dashboard:login")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, _("You have been logged out."))
        return super().dispatch(request, *args, **kwargs)


class ProfileView(DashboardAccessMixin, View):
    template_name = "dashboard/profile.html"

    def get(self, request):
        return render(request, self.template_name, {
            "profile_form": ProfileForm(instance=request.user),
            "password_form": PasswordChangeDashboardForm(user=request.user),
        })

    def post(self, request):
        action = request.POST.get("action", "profile")
        if action == "password":
            password_form = PasswordChangeDashboardForm(request.user, request.POST)
            profile_form = ProfileForm(instance=request.user)
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data["new_password"])
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, _("Password updated successfully."))
                return redirect("dashboard:profile")
            return render(request, self.template_name, {
                "profile_form": profile_form,
                "password_form": password_form,
            })

        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
        password_form = PasswordChangeDashboardForm(user=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, _("Profile updated successfully."))
            return redirect("dashboard:profile")
        return render(request, self.template_name, {
            "profile_form": profile_form,
            "password_form": password_form,
        })


class RolesPermissionsView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/roles.html"
    module_key = "users"

    def get_context_data(self, **kwargs):
        from apps.dashboard.roles import MODULES, ROLE_MODULES

        context = super().get_context_data(**kwargs)
        context["role_matrix"] = [
            (role, sorted(modules))
            for role, modules in ROLE_MODULES.items()
        ]
        context["modules"] = MODULES
        return context


class AuditLogView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/audit_logs.html"
    module_key = "users"
