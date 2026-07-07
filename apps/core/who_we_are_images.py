"""Assign photos to the homepage and Who we are page about sections."""

import os
from pathlib import Path

from django.conf import settings
from django.core.files import File

from apps.core.homepage_content import WHO_WE_ARE_KEY, sync_who_we_are_section
from apps.core.models import HomepageSection
from apps.pages.models import Counsellor, LeadershipMember, Page

# Ministry-appropriate photos already stored locally (preferred order).
LOCAL_FALLBACKS = [
    "team/-ERA_74-scaled-1-790x1024.jpg",
    "counsellors/-ERA_74-scaled-1-790x1024.jpg",
    "counsellors/yves-gashugi.jpg",
    "team/DSC_4945-1-806x1024.png",
    "team/WhatsApp-Image-2023-12-15-at-23.15.37_19b340dd.jpg",
    "team/WhatsApp-Image-2023-12-15-at-23.36.31_1e97452f-1.jpg",
]

PAGE_FALLBACKS = [
    "team/-ERA_74-scaled-1-790x1024.jpg",
    "team/DSC_4945-1-806x1024.png",
    "team/WhatsApp-Image-2023-12-15-at-23.15.37_19b340dd.jpg",
    "counsellors/-ERA_74-scaled-1-790x1024.jpg",
]


def _media_file(relative_path):
    path = Path(settings.MEDIA_ROOT) / relative_path
    return path if path.is_file() else None


def _leader_photo_path():
    yves = (
        LeadershipMember.objects.filter(is_active=True)
        .exclude(photo="")
        .filter(name__icontains="yves")
        .first()
    )
    if yves and yves.photo:
        return Path(yves.photo.path)

    leader = LeadershipMember.objects.exclude(photo="").order_by("order", "name").first()
    if leader and leader.photo:
        return Path(leader.photo.path)
    return None


def _counsellor_photo_path():
    counsellor = Counsellor.objects.filter(is_active=True).exclude(photo="").order_by("order").first()
    if counsellor and counsellor.photo:
        return Path(counsellor.photo.path)
    return None


def _first_local_path(candidates):
    for relative in candidates:
        path = _media_file(relative)
        if path:
            return path
    return None


def resolve_homepage_image_path():
    return (
        _leader_photo_path()
        or _counsellor_photo_path()
        or _first_local_path(LOCAL_FALLBACKS)
    )


def resolve_page_image_path():
    return (
        _leader_photo_path()
        or _first_local_path(PAGE_FALLBACKS)
        or _counsellor_photo_path()
    )


def _assign_image(instance, field_name, source_path, force=False):
    current = getattr(instance, field_name, None)
    if current and not force:
        return False
    if not source_path or not Path(source_path).is_file():
        return False

    filename = os.path.basename(str(source_path))
    with open(source_path, "rb") as handle:
        getattr(instance, field_name).save(filename, File(handle), save=True)
    return True


def import_who_we_are_images(force=False):
    """Attach ministry photos to the homepage block and Who we are page."""
    sync_who_we_are_section()
    results = {"homepage": False, "page": False}

    section = HomepageSection.objects.filter(key=WHO_WE_ARE_KEY).first()
    homepage_source = resolve_homepage_image_path()
    if section and homepage_source:
        results["homepage"] = _assign_image(section, "image", homepage_source, force=force)

    page = Page.objects.filter(slug_en="who-we-are").first()
    page_source = resolve_page_image_path()
    if page and page_source:
        results["page"] = _assign_image(page, "featured_image", page_source, force=force)

    return results, homepage_source, page_source
