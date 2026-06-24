import secrets
import string

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView

from apps.dashboard.forms import UserCreateForm, UserEditForm
from apps.dashboard.permissions import UserManagementMixin
from apps.dashboard.roles import user_can_manage_target_user

User = get_user_model()


class UserListView(UserManagementMixin, ListView):
    template_name = "dashboard/users/list.html"
    context_object_name = "users"
    paginate_by = 25

    def get_queryset(self):
        qs = User.objects.order_by("-date_joined")
        actor = self.request.user
        if not actor.is_superuser:
            qs = qs.exclude(is_superuser=True).exclude(role=User.ROLE_SUPER_ADMIN)
        search = self.request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        role = self.request.GET.get("role")
        if role:
            qs = qs.filter(role=role)
        status = self.request.GET.get("status")
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        return qs


class UserCreateView(UserManagementMixin, View):
    template_name = "dashboard/users/form.html"

    def get(self, request):
        form = UserCreateForm(actor=request.user)
        return render(request, self.template_name, {"form": form, "is_create": True})

    def post(self, request):
        form = UserCreateForm(request.POST, request.FILES, actor=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, _("User created successfully."))
            return redirect("dashboard:user_edit", pk=user.pk)
        return render(request, self.template_name, {"form": form, "is_create": True})


class UserEditView(UserManagementMixin, View):
    template_name = "dashboard/users/form.html"

    def get_target(self, pk):
        target = get_object_or_404(User, pk=pk)
        if not user_can_manage_target_user(self.request.user, target):
            raise PermissionDenied
        return target

    def get(self, request, pk):
        target = self.get_target(pk)
        form = UserEditForm(instance=target, actor=request.user)
        return render(request, self.template_name, {"form": form, "target_user": target, "is_create": False})

    def post(self, request, pk):
        target = self.get_target(pk)
        form = UserEditForm(request.POST, request.FILES, instance=target, actor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("User updated successfully."))
            return redirect("dashboard:user_edit", pk=target.pk)
        return render(request, self.template_name, {"form": form, "target_user": target, "is_create": False})


class UserToggleActiveView(UserManagementMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if not user_can_manage_target_user(request.user, target):
            raise PermissionDenied
        if target.pk == request.user.pk:
            messages.error(request, _("You cannot deactivate your own account."))
            return redirect("dashboard:user_list")
        target.is_active = not target.is_active
        target.save(update_fields=["is_active"])
        messages.success(
            request,
            _("User activated.") if target.is_active else _("User deactivated."),
        )
        return redirect("dashboard:user_list")


class UserResetPasswordView(UserManagementMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if not user_can_manage_target_user(request.user, target):
            raise PermissionDenied
        alphabet = string.ascii_letters + string.digits
        temp_password = "".join(secrets.choice(alphabet) for _ in range(12))
        target.set_password(temp_password)
        target.save(update_fields=["password"])
        messages.success(
            request,
            _("Temporary password for %(user)s: %(password)s") % {
                "user": target.username,
                "password": temp_password,
            },
        )
        return redirect("dashboard:user_edit", pk=target.pk)


class UserDeleteView(UserManagementMixin, View):
    def post(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied
        target = get_object_or_404(User, pk=pk)
        if target.pk == request.user.pk:
            messages.error(request, _("You cannot delete your own account."))
            return redirect("dashboard:user_list")
        username = target.username
        target.delete()
        messages.success(request, _("User %(name)s deleted.") % {"name": username})
        return redirect("dashboard:user_list")
