from django.http import HttpResponsePermanentRedirect

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
