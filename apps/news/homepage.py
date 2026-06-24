"""Homepage and listing post queries with strict per-language filtering."""

import re

from django.db.models import Q
from django.utils.translation import get_language

from .models import Post, Category

DEMO_CONTENT_MARKER = "demonstration article is ready to be replaced"

LANGUAGE_CODES = Post.LANGUAGE_CODES


def normalize_language_code(language_code=None):
    language = (language_code or get_language() or "en").split("-")[0]
    if language not in LANGUAGE_CODES:
        return "en"
    return language


def is_demo_post(post):
    for field in ("content", "content_en", "content_fr", "content_rw"):
        value = getattr(post, field, None) or ""
        if DEMO_CONTENT_MARKER in value:
            return True
    return False


def demo_post_q():
    return (
        Q(content__icontains=DEMO_CONTENT_MARKER)
        | Q(content_en__icontains=DEMO_CONTENT_MARKER)
        | Q(content_fr__icontains=DEMO_CONTENT_MARKER)
        | Q(content_rw__icontains=DEMO_CONTENT_MARKER)
    )


def _nonempty_q(field_name):
    return ~Q(**{field_name: ""}) & ~Q(**{field_name: None})


def post_available_in_language_q(language_code):
    """
    Return Q for posts that have real content in the requested language.
    No cross-language fallback for listings.
    """
    lang = normalize_language_code(language_code)
    title_field = f"title_{lang}"
    content_field = f"content_{lang}"

    translated = _nonempty_q(title_field) & _nonempty_q(content_field)

    if lang == "en":
        legacy_english = (
            (Q(title_en__isnull=True) | Q(title_en=""))
            & (Q(content_en__isnull=True) | Q(content_en=""))
            & _nonempty_q("title")
            & _nonempty_q("content")
            & (
                Q(source_language="en")
                | Q(source_language="")
                | Q(source_language__isnull=True)
            )
        )
        translated = translated | legacy_english

    return translated


def posts_for_language(language_code=None):
    """
    Return only real published posts available in the requested language.
    No demo posts. No cross-language fallback.
    """
    lang = normalize_language_code(language_code)
    return (
        Post.objects.filter(status=Post.STATUS_PUBLISHED)
        .filter(post_available_in_language_q(lang))
        .exclude(demo_post_q())
        .select_related("category", "author")
        .order_by("-published_at", "-created_at")
    )


def published_posts_queryset(language_code=None):
    """Alias used by legacy callers; always language-scoped."""
    return posts_for_language(language_code)


HOME_CATEGORY_SLUGS = {
    "church": {"en": "church", "fr": "itorero", "rw": "itorero"},
    "leadership": {"en": "leadership", "fr": "ubuyobozi", "rw": "ubuyobozi"},
    "family": {"en": "family", "fr": "umuryango", "rw": "umuryango"},
    "constructive-criticism": {
        "en": "constructive-criticism",
        "fr": "constructive-criticism",
        "rw": "ubusesenguzi",
    },
    "healing": {"en": "healing", "fr": "isanamitima", "rw": "isanamitima"},
}


def category_for_home_section(section_key, language=None):
    """Resolve a homepage category block to a real Category for the active language."""
    lang = normalize_language_code(language)
    slug_map = HOME_CATEGORY_SLUGS.get(section_key, {})
    slug = slug_map.get(lang) or slug_map.get("en")
    if not slug:
        return None

    return (
        Category.objects.filter(is_active=True)
        .filter(
            Q(slug=slug)
            | Q(slug_en=slug)
            | Q(slug_fr=slug)
            | Q(slug_rw=slug)
        )
        .order_by("pk")
        .first()
    )


def posts_for_home_section(section_key, limit, language=None):
    """Language-scoped posts for a homepage category section."""
    lang = normalize_language_code(language)
    category = category_for_home_section(section_key, lang)
    if not category:
        return []
    return list(posts_for_language(lang).filter(category=category)[:limit])


def strip_html(value):
    return re.sub(r"<[^>]+>", "", value or "").strip()


def post_has_language_content(post, language_code):
    """Python-level check mirroring queryset rules."""
    lang = normalize_language_code(language_code)
    title = (post.field_for_language("title", lang, fallback=False) or "").strip()
    content = strip_html(post.field_for_language("content", lang, fallback=False))
    if title and content:
        return True
    if lang == "en":
        legacy_title = (post.title or "").strip()
        legacy_content = strip_html(post.content)
        legacy_en = not (post.title_en or "").strip() and not strip_html(post.content_en)
        source_ok = post.source_language in ("en", "", None) if hasattr(post, "source_language") else legacy_en
        return bool(legacy_title and legacy_content and legacy_en and source_ok)
    if hasattr(post, "source_language") and post.source_language == lang:
        return bool(title and content)
    return False


def available_languages_for_post(post):
    return [lang for lang in LANGUAGE_CODES if post_has_language_content(post, lang)]
