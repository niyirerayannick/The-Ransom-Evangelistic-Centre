"""Parse counsellor profile from the legacy WordPress find-a-counsellor page."""

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

FIND_COUNSELLOR_URL = "https://yvesgashugi.org/find-a-counsellor/"


def fetch_page_html(url=FIND_COUNSELLOR_URL, timeout=30):
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "REC-Site-Importer/1.0"})
    response.raise_for_status()
    return response.text


def _clean_text(value):
    return re.sub(r"\s+", " ", (value or "").strip())


def _first_image_src(soup, keywords=("yves", "gashugi", "counsellor", "psychologist")):
    for img in soup.select("img[src]"):
        src = (img.get("src") or "").strip()
        alt = (img.get("alt") or "").lower()
        if not src or "logo" in src.lower() or "icon" in src.lower():
            continue
        if any(word in alt for word in keywords) or any(word in src.lower() for word in keywords):
            return urljoin(FIND_COUNSELLOR_URL, src)
    for img in soup.select("img[src]"):
        src = (img.get("src") or "").strip()
        if src and "wp-content/uploads" in src:
            return urljoin(FIND_COUNSELLOR_URL, src)
    return ""


def parse_counsellor_page(html):
    soup = BeautifulSoup(html, "html.parser")
    name = ""
    role = ""
    bio_parts = []

    for heading in soup.select("h1, h2, h3, h4, h5, h6, strong, b"):
        text = _clean_text(heading.get_text(" ", strip=True))
        if not name and re.search(r"yves", text, re.I):
            name = text
            continue
        if name and not role and re.search(r"psychologist|clinical|trauma|conseiller", text, re.I):
            role = text

    for paragraph in soup.select("p"):
        text = _clean_text(paragraph.get_text(" ", strip=True))
        if len(text) < 40:
            continue
        if re.search(r"psychologist|trauma|listening|potential|counsellor|counselor", text, re.I):
            bio_parts.append(text)

    bio = " ".join(bio_parts[:3])
    if bio:
        bio = "".join(f"<p>{part}</p>" for part in bio_parts[:3])
    photo_url = _first_image_src(soup)
    return {
        "name": name or "Yves GASHUGI",
        "role": role or "Clinical Psychologist specializing in trauma",
        "bio": bio,
        "photo_url": photo_url,
    }
