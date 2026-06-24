from django import template
from django.urls import reverse
from django.utils import translation

from apps.core.language_flags import LANGUAGE_CODES, LANGUAGE_META
from apps.news.i18n_urls import (
    category_url_for_language,
    post_url_for_language,
    prefix_language_url,
    localize_news_category_path,
)

register = template.Library()


@register.simple_tag(takes_context=True)
def translated_url(context, language_code):
    request = context.get("request")
    post = context.get("post")
    category = context.get("category")

    if post and hasattr(post, "slug_for_language"):
        url = post_url_for_language(post, language_code)
        if url:
            return url
        with translation.override(language_code):
            return reverse("home")

    if category and hasattr(category, "slug_en"):
        return category_url_for_language(category, language_code)

    if not request:
        with translation.override(language_code):
            return reverse("home")

    path = request.path
    parts = path.lstrip("/").split("/", 1)
    suffix = parts[1] if len(parts) > 1 and parts[0] in {"en", "fr", "rw"} else path.lstrip("/")

    if suffix.startswith("news/category/"):
        localized_suffix = localize_news_category_path(f"/{suffix}", language_code).lstrip("/")
        return prefix_language_url(f"/{localized_suffix}", language_code)

    if suffix.startswith("news/") and context.get("post"):
        url = post_url_for_language(context["post"], language_code)
        if url:
            return url

    return prefix_language_url(f"/{suffix}" if suffix else "/", language_code)


@register.simple_tag(takes_context=True)
def language_switcher_links(context):
    """Return language links for the header switcher with availability flags."""
    request = context.get("request")
    post = context.get("post")
    category = context.get("category")
    links = []

    for code in LANGUAGE_CODES:
        meta = LANGUAGE_META[code]
        base = {
            "code": code,
            "label": meta["label"],
            "flag_url": meta["flag_url"],
            "flag_iso": meta["flag_iso"],
        }
        if post and hasattr(post, "is_available_in_language"):
            available = post.is_available_in_language(code)
            if post and not available:
                with translation.override(code):
                    url = reverse("home")
            else:
                url = None
                if post:
                    url = post_url_for_language(post, code)
                if not url:
                    with translation.override(code):
                        url = reverse("home")
            links.append({
                **base,
                "url": url,
                "available": available if post else True,
            })
            continue

        if category:
            url = category_url_for_language(category, code)
            links.append({**base, "url": url, "available": True})
            continue

        path = request.path if request else "/"
        parts = path.lstrip("/").split("/", 1)
        suffix = parts[1] if len(parts) > 1 and parts[0] in {"en", "fr", "rw"} else path.lstrip("/")
        if suffix.startswith("news/category/"):
            localized = localize_news_category_path(f"/{suffix}", code).lstrip("/")
            url = prefix_language_url(f"/{localized}", code)
        else:
            url = prefix_language_url(f"/{suffix}" if suffix else "/", code)
        links.append({**base, "url": url, "available": True})

    return links
