"""URL helpers for multilingual news routes."""

from django.urls import reverse
from django.utils import translation

from .homepage import HOME_CATEGORY_SLUGS, normalize_language_code

CATEGORY_SECTION_BY_SLUG = {}
for section_key, slug_map in HOME_CATEGORY_SLUGS.items():
    for slug in slug_map.values():
        if slug:
            CATEGORY_SECTION_BY_SLUG[slug] = section_key


def localize_news_category_path(url, language=None):
    """Rewrite /news/category/<slug>/ to the slug for the requested language."""
    if "/news/category/" not in (url or ""):
        return url
    language = normalize_language_code(language)
    slug_part = url.split("/news/category/")[-1].strip("/").split("/")[0]
    section_key = CATEGORY_SECTION_BY_SLUG.get(slug_part)
    if not section_key:
        for key, slug_map in HOME_CATEGORY_SLUGS.items():
            if slug_part in slug_map.values():
                section_key = key
                break
    if not section_key:
        return url
    slug_map = HOME_CATEGORY_SLUGS[section_key]
    new_slug = slug_map.get(language) or slug_map.get("en")
    return f"/news/category/{new_slug}/"


def category_slug_for_language(category, language=None):
    """Return the slug for a category in the requested language, or empty string."""
    language = normalize_language_code(language)
    slug = (getattr(category, f"slug_{language}", None) or "").strip()
    if slug:
        return slug

    category_slugs = {
        s for s in (
            category.slug,
            getattr(category, "slug_en", None),
            getattr(category, "slug_fr", None),
            getattr(category, "slug_rw", None),
        ) if s
    }
    for slug_map in HOME_CATEGORY_SLUGS.values():
        if category_slugs & set(slug_map.values()):
            return (slug_map.get(language) or "").strip()
    return ""


def category_url_for_language(category, language=None):
    language = normalize_language_code(language)
    slug = category_slug_for_language(category, language)
    with translation.override(language):
        if slug:
            return reverse("news:category_detail", kwargs={"slug": slug})
        return reverse("news:post_list")


def post_url_for_language(post, language=None):
    language = normalize_language_code(language)
    if not post.is_available_in_language(language):
        return None
    slug = post.slug_for_language(language, fallback=False)
    if not slug:
        return None
    with translation.override(language):
        if post.published_at:
            return reverse(
                "news:post_detail",
                kwargs={
                    "year": post.published_at.year,
                    "month": post.published_at.month,
                    "day": post.published_at.day,
                    "slug": slug,
                },
            )
        return reverse("news:post_detail_slug", kwargs={"slug": slug})


def prefix_language_url(url, language):
    language = normalize_language_code(language)
    if not url or url == "#":
        return f"/{language}/"
    if url.startswith(("http://", "https://", "//")):
        return url
    if url == "/":
        return f"/{language}/"
    if url.startswith(f"/{language}/"):
        return url
    for code in ("en", "fr", "rw"):
        if url.startswith(f"/{code}/"):
            return f"/{language}/{url[len(code) + 2:]}"
    return f"/{language}{url}" if url.startswith("/") else url
