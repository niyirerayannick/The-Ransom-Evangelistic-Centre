"""Parse team members from the legacy WordPress our-team page."""

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

OUR_TEAM_URL = "https://yvesgashugi.org/our-team/"
GENERIC_SOCIAL_HOSTS = {
    "facebook.com",
    "www.facebook.com",
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",
    "instagram.com",
    "www.instagram.com",
    "linkedin.com",
    "www.linkedin.com",
}


def normalize_name(value):
    return re.sub(r"\s+", " ", (value or "").strip())


def slug_from_name(name):
    from django.utils.text import slugify

    return slugify(normalize_name(name))[:200] or "member"


def is_generic_social_url(url):
    if not url:
        return True
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").strip("/")
    if host in GENERIC_SOCIAL_HOSTS and not path:
        return True
    return False


def social_url(url, network):
    if not url or is_generic_social_url(url):
        return ""
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if network == "facebook" and "facebook" in host:
        return url
    if network == "x" and ("twitter" in host or host.endswith("x.com")):
        return url
    if network == "instagram" and "instagram" in host:
        return url
    if network == "linkedin" and "linkedin" in host:
        return url
    return ""


def detect_social_from_link(anchor, href):
    href = (href or "").strip()
    if not href or href.startswith("#"):
        return None, ""
    label = (anchor.get("aria-label") or "").lower()
    icon_class = " ".join(anchor.select_one("i, svg")["class"]) if anchor.select_one("i, svg") else ""
    icon_class = icon_class.lower()
    if href.startswith("mailto:"):
        return "email", href.replace("mailto:", "").strip()
    if href.startswith("tel:"):
        return "phone", href.replace("tel:", "").strip()
    if "facebook" in label or "facebook" in icon_class:
        return "facebook", href
    if "twitter" in label or "twitter" in icon_class or "x.com" in href:
        return "x", href
    if "instagram" in label or "instagram" in icon_class:
        return "instagram", href
    if "linkedin" in label or "linkedin" in icon_class:
        return "linkedin", href
    return None, href


def fetch_team_page_html(url=OUR_TEAM_URL, timeout=45):
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "Mozilla/5.0 (compatible; RECSiteImporter/1.0)"},
    )
    response.raise_for_status()
    return response.text


def parse_team_members(html):
    soup = BeautifulSoup(html, "html.parser")
    members = []
    seen = set()

    widgets = soup.select(".elementor-widget-elementskit-team")
    if not widgets:
        return []

    order = 0
    for widget in widgets:
        popup = widget.select_one(".elementskit-team-popup, .zoom-anim-dialog")
        name_el = widget.select_one(
            ".ekit-team-modal-title, h2, h3, .elementskit-team-name, .profile-title"
        )
        role_el = widget.select_one(
            ".ekit-team-modal-position, .elementskit-team-position, p, .profile-designation"
        )
        name = normalize_name(name_el.get_text() if name_el else "")
        if not name or name.lower() in {"meet our team", "quick links", "contact us", "location"}:
            continue
        if len(name) > 80:
            continue

        key = slug_from_name(name)
        if key in seen:
            continue

        role = ""
        if popup:
            popup_role = popup.select_one(".ekit-team-modal-position")
            if popup_role:
                role = normalize_name(popup_role.get_text())
        if not role and role_el:
            candidate = normalize_name(role_el.get_text())
            if candidate and len(candidate) < 60:
                role = candidate

        photos = []
        for img in widget.select("img"):
            src = (img.get("src") or "").strip()
            if not src or "/uploads/" not in src:
                continue
            if any(skip in src.lower() for skip in ("ransom", "placeholder")):
                continue
            photos.append(src)
        photo_url = photos[0] if photos else ""

        bio = ""
        if popup:
            bio_el = popup.select_one(".ekit-team-modal-content")
            if bio_el:
                bio = bio_el.get_text(" ", strip=True)
            if not bio or len(bio) < 40:
                for paragraph in popup.select("p"):
                    text = paragraph.get_text(" ", strip=True)
                    if len(text) > 80:
                        bio = text
                        break

        email = ""
        phone = ""
        social = {"facebook_url": "", "x_url": "", "instagram_url": "", "linkedin_url": ""}
        search_root = popup or widget
        for anchor in search_root.select("a[href]"):
            kind, value = detect_social_from_link(anchor, anchor.get("href"))
            if kind == "email" and value and not email:
                email = value
            elif kind == "phone" and value and not phone:
                phone = re.sub(r"\s+", " ", value.strip())
            elif kind == "facebook" and value:
                social["facebook_url"] = social_url(value, "facebook") or social["facebook_url"]
            elif kind == "x" and value:
                social["x_url"] = social_url(value, "x") or social["x_url"]
            elif kind == "instagram" and value:
                social["instagram_url"] = social_url(value, "instagram") or social["instagram_url"]
            elif kind == "linkedin" and value:
                social["linkedin_url"] = social_url(value, "linkedin") or social["linkedin_url"]

        if not role and not photo_url and not bio:
            continue

        seen.add(key)
        members.append({
            "slug": key,
            "name": name,
            "role": role,
            "photo_url": photo_url,
            "bio": bio,
            "email": email,
            "phone": phone,
            **social,
            "order": order,
        })
        order += 10

    return members
