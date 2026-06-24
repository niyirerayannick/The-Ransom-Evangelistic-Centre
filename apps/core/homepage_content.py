"""Default copy and sync helpers for homepage content blocks."""

from apps.core.models import HomepageSection

WHO_WE_ARE_KEY = "who-we-are"

WHO_WE_ARE_DEFAULTS = {
    "subtitle_en": "Who we are",
    "subtitle_fr": "Qui sommes-nous",
    "subtitle_rw": "Abo turi bo",
    "title_en": "THE RANSOM EVANGELISTIC CENTRE Abbreviated as “REC”",
    "title_fr": "THE RANSOM EVANGELISTIC CENTRE Abrégé en « REC »",
    "title_rw": "THE RANSOM EVANGELISTIC CENTRE YagufiSHA nka « REC »",
    "content_en": (
        "<p>Founded in 2023, REC exists to inform the Gospel of Jesus Christ in all lens "
        "with the aim of equipping the church and helping believers and unbelievers believe "
        "with true wisdom through articles writing and every other effective means that bring salvation.</p>"
    ),
    "content_fr": (
        "<p>Fondé en 2023, REC existe pour annoncer l’Évangile de Jésus-Christ sous toutes ses dimensions, "
        "dans le but d’équiper l’Église et d’aider croyants et non-croyants à croire avec une vraie sagesse "
        "par la rédaction d’articles et tout autre moyen efficace qui conduit au salut.</p>"
    ),
    "content_rw": (
        "<p>Yashinzwe mu 2023, REC igamije kwamamaza Ubutumwa Bwiza bwa Yesu Kristo mu buryo bwuzuye, "
        "ifite intego yo gukomeza Itorero no gufasha abizera n’abatarizera kwizera mu bwenge nyakuri "
        "binyuze mu kwandika inyandiko n’ubundi buryo buhanitse bugana ku gakiza.</p>"
    ),
    "button_text_en": "FIND A COUNSELLOR",
    "button_text_fr": "TROUVER UN CONSEILLER",
    "button_text_rw": "SHAKA UMUJYANAMA",
    "button_url": "find-a-counsellor",
    "section_type": "featured",
    "is_active": True,
    "order": 10,
}


def _migrate_legacy_fields(section):
    for field in ("title", "subtitle", "content", "button_text"):
        base = getattr(section, field, None)
        en_field = f"{field}_en"
        if base and not getattr(section, en_field, None):
            setattr(section, en_field, base)


def sync_who_we_are_section(force=False):
    """Create or fill the homepage Who we are block with EN/FR/RW copy."""
    section, created = HomepageSection.objects.get_or_create(
        key=WHO_WE_ARE_KEY,
        defaults={
            "title": WHO_WE_ARE_DEFAULTS["title_en"],
            "subtitle": WHO_WE_ARE_DEFAULTS["subtitle_en"],
            "content": WHO_WE_ARE_DEFAULTS["content_en"],
            "button_text": WHO_WE_ARE_DEFAULTS["button_text_en"],
            "button_url": WHO_WE_ARE_DEFAULTS["button_url"],
            "section_type": WHO_WE_ARE_DEFAULTS["section_type"],
            "is_active": True,
            "order": WHO_WE_ARE_DEFAULTS["order"],
        },
    )

    _migrate_legacy_fields(section)
    updated_fields = []
    for field, value in WHO_WE_ARE_DEFAULTS.items():
        if field == "is_active":
            continue
        current = getattr(section, field, None)
        if created or force or not current:
            setattr(section, field, value)
            updated_fields.append(field)

    if updated_fields or created:
        section.save()
    return section


def resolve_homepage_button_url(button_url, language=None):
    """Resolve a page key or slug to a language-aware counsellor/page URL."""
    from django.urls import reverse
    from django.utils import translation as trans
    from django.utils.translation import get_language

    from apps.news.homepage import normalize_language_code
    from apps.pages.site_defaults import PAGE_SPECS

    lang = normalize_language_code(language or get_language())
    raw = (button_url or "find-a-counsellor").strip()

    if raw.startswith(("http://", "https://", "//")):
        return raw

    page_key = raw.strip("/").replace("page/", "")
    spec = next((s for s in PAGE_SPECS if s["key"] == page_key), None)
    if not spec:
        for candidate in PAGE_SPECS:
            if page_key in candidate.get("source_slugs", []) or page_key in candidate["slug"].values():
                spec = candidate
                break

    slug = spec["slug"].get(lang) or spec["slug"]["en"] if spec else page_key
    with trans.override(lang):
        return reverse("pages:page_detail", kwargs={"slug": slug})
