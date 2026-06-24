from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .roles import user_can_access_module, user_can_manage_users, user_can_write_module


def dashboard_access_required(view_func):
    @wraps(view_func)
    @login_required(login_url="/dashboard/login/")
    def wrapper(request, *args, **kwargs):
        if not request.user.can_access_dashboard():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


class DashboardAccessMixin:
    login_url = "/dashboard/login/"
    module_key = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url=self.login_url)
        if not request.user.is_active:
            raise PermissionDenied
        if not request.user.can_access_dashboard():
            raise PermissionDenied
        if self.module_key and not user_can_access_module(request.user, self.module_key):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ModuleWriteMixin(DashboardAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url=self.login_url)
        if not request.user.is_active:
            raise PermissionDenied
        if not request.user.can_access_dashboard():
            raise PermissionDenied
        if self.module_key and not user_can_access_module(request.user, self.module_key):
            raise PermissionDenied
        if request.method not in ("GET", "HEAD", "OPTIONS") and self.module_key:
            if not user_can_write_module(request.user, self.module_key):
                raise PermissionDenied
        return super(DashboardAccessMixin, self).dispatch(request, *args, **kwargs)


class UserManagementMixin(DashboardAccessMixin):
    module_key = "users"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url=self.login_url)
        if not user_can_manage_users(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PostAccessMixin(DashboardAccessMixin):
    module_key = "posts"

    def get_post_queryset(self):
        from apps.news.models import Post

        queryset = Post.objects.select_related("category", "author", "reviewed_by").prefetch_related("tags")
        user = self.request.user
        if user.is_superuser or user.role in ("super_admin", "admin", "editor", "viewer"):
            return queryset
        return queryset.filter(author=user)

    def get_post(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(self.get_post_queryset(), pk=self.kwargs["pk"])
