"""Maintenance mode helpers."""

from django.conf import settings as django_settings
from django.utils import timezone
from django.utils.translation import get_language

from apps.core.language_flags import LANGUAGE_CODES, LANGUAGE_META

DEFAULT_MAINTENANCE_COPY = {
    "en": {
        "title": "Our Website is Coming Soon",
        "message": "We are working hard to bring you a better experience. Please check back soon.",
    },
    "fr": {
        "title": "Notre site arrive bientôt",
        "message": "Nous travaillons pour vous offrir une meilleure expérience. Revenez bientôt.",
    },
    "rw": {
        "title": "Urubuga rwacu ruri hafi gufungurwa",
        "message": "Turimo gutegura urubuga rwiza kurushaho. Muzagaruke vuba.",
    },
}


def get_site_setting():
    from apps.core.models import SiteSetting

    return SiteSetting.objects.first()


def is_maintenance_mode_enabled():
    site = get_site_setting()
    if site is not None:
        return bool(site.maintenance_mode)
    return bool(getattr(django_settings, "MAINTENANCE_MODE", False))


def user_can_preview_during_maintenance(user):
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    from apps.dashboard.roles import effective_role

    return effective_role(user) in {"super_admin", "admin"}


def maintenance_field_for_language(site, field_name, language=None):
    lang = (language or get_language() or "en").split("-")[0]
    if lang not in LANGUAGE_CODES:
        lang = "en"
    if site:
        value = getattr(site, f"{field_name}_{lang}", None) or getattr(site, field_name, None) or ""
        if value:
            return value
        value = getattr(site, f"{field_name}_en", None) or ""
        if value:
            return value
    return DEFAULT_MAINTENANCE_COPY.get(lang, DEFAULT_MAINTENANCE_COPY["en"]).get(
        "title" if field_name == "maintenance_title" else "message", ""
    )


def build_maintenance_context(request):
    site = get_site_setting()
    language = (get_language() or "en").split("-")[0]
    if language not in LANGUAGE_CODES:
        language = "en"

    launch_at = site.maintenance_expected_launch_date if site else None
    show_countdown = bool(site and site.maintenance_show_countdown and launch_at)
    contact_email = ""
    if site:
        contact_email = (
            site.maintenance_contact_email
            or site.contact_email
            or site.email
            or ""
        )

    language_links = [
        {
            "code": code,
            "label": LANGUAGE_META[code]["label"],
            "flag_url": LANGUAGE_META[code]["flag_url"],
            "url": f"/{code}/",
            "active": code == language,
        }
        for code in LANGUAGE_CODES
    ]

    social_links = []
    if site:
        for label, url in (
            ("Facebook", site.facebook_url),
            ("X", site.x_url or site.twitter_url),
            ("Instagram", site.instagram_url),
            ("YouTube", site.youtube_url),
        ):
            if url:
                social_links.append({"label": label, "url": url})

    return {
        "site_settings": site,
        "maintenance_title": maintenance_field_for_language(site, "maintenance_title", language),
        "maintenance_message": maintenance_field_for_language(site, "maintenance_message", language),
        "maintenance_contact_email": contact_email,
        "maintenance_show_countdown": show_countdown,
        "maintenance_launch_iso": launch_at.isoformat() if launch_at else "",
        "maintenance_launch_timestamp": int(launch_at.timestamp() * 1000) if launch_at else None,
        "language_links": language_links,
        "social_links": social_links,
        "copyright_text": (
            getattr(site, f"copyright_text_{language}", None)
            or getattr(site, "copyright_text_en", None)
            or getattr(site, "copyright_text", None)
            or f"© {timezone.now().year} The Ransom Evangelistic Centre"
        ),
    }


def retry_after_seconds(launch_at):
    if not launch_at:
        return None
    now = timezone.now()
    if launch_at <= now:
        return None
    delta = launch_at - now
    return max(int(delta.total_seconds()), 60)
