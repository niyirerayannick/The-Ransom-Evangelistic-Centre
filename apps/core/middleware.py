from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render
from django.utils import translation

from .maintenance import (
    build_maintenance_context,
    is_maintenance_mode_enabled,
    retry_after_seconds,
    user_can_preview_during_maintenance,
)
from .models import Redirect


class LegacyRedirectMiddleware:
    """Resolve imported WordPress URLs before Django's normal URL routing."""

    language_codes = {"en", "fr", "rw"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        parts = path.lstrip("/").split("/", 1)
        if parts and parts[0] in self.language_codes:
            return self.get_response(request)
        language = "en"
        unprefixed_path = path

        redirect = Redirect.objects.filter(
            is_active=True,
            source_language=language,
            old_url__endswith=unprefixed_path,
        ).first()
        if redirect and redirect.new_url not in {path, unprefixed_path}:
            return HttpResponsePermanentRedirect(redirect.new_url)

        return self.get_response(request)


class MaintenanceModeMiddleware:
    """Show a coming-soon page to public visitors when maintenance mode is enabled."""

    ALLOWED_PREFIXES = (
        "/dashboard",
        "/admin",
        "/static",
        "/media",
        "/ckeditor",
    )
    ALLOWED_EXACT = {
        "/favicon.ico",
        "/robots.txt",
        "/health",
        "/health/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not is_maintenance_mode_enabled():
            return self.get_response(request)

        path = request.path or "/"
        if self._is_allowed_path(path):
            return self.get_response(request)

        if user_can_preview_during_maintenance(request.user):
            return self.get_response(request)

        return self._maintenance_response(request)

    def _is_allowed_path(self, path):
        if path in self.ALLOWED_EXACT:
            return True
        return any(path.startswith(prefix) for prefix in self.ALLOWED_PREFIXES)

    def _maintenance_response(self, request):
        parts = request.path.lstrip("/").split("/", 1)
        if parts and parts[0] in {"en", "fr", "rw"}:
            language = parts[0]
        else:
            language = translation.get_language() or "en"

        with translation.override(language):
            context = build_maintenance_context(request)
            site = context.get("site_settings")
            launch_at = site.maintenance_expected_launch_date if site else None
            response = render(request, "core/maintenance.html", context, status=503)
            response["Retry-After"] = str(retry_after_seconds(launch_at) or 3600)
            return response
