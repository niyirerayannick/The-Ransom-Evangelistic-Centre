import json
import re
from html import unescape
from urllib.parse import urljoin

import requests
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.html import strip_tags

from apps.core.models import SiteSetting
from apps.pages.models import Page
from apps.pages.site_defaults import PAGE_SPECS


SOURCES = {
    "en": "https://yvesgashugi.org/",
    "fr": "https://fra.yvesgashugi.org/",
    "rw": "https://kiny.yvesgashugi.org/",
}


class Command(BaseCommand):
    help = "Fetch and map multilingual pages from the current WordPress websites."

    def add_arguments(self, parser):
        parser.add_argument("--no-seed", action="store_true", help="Do not seed defaults before importing.")
        parser.add_argument("--timeout", type=int, default=30)

    def handle(self, *args, **options):
        if not options["no_seed"]:
            call_command("seed_site_pages")

        fetched = {}
        for language, base_url in SOURCES.items():
            try:
                fetched[language] = self._fetch_pages(base_url, options["timeout"])
                self.stdout.write(self.style.SUCCESS(
                    f"{language}: fetched {len(fetched[language])} WordPress pages"
                ))
            except (requests.RequestException, json.JSONDecodeError) as exc:
                fetched[language] = []
                self.stdout.write(self.style.WARNING(
                    f"{language}: source unavailable ({exc}); existing translated fallback retained"
                ))

        self._import_site_settings(SOURCES["en"], options["timeout"])

        updated = 0
        for spec in PAGE_SPECS:
            page = Page.objects.filter(slug_en=spec["slug"]["en"]).first()
            if not page:
                continue
            for language, source_pages in fetched.items():
                match = self._match_page(spec, source_pages)
                if not match:
                    continue
                content = self._clean_content(match["content"]["rendered"], SOURCES[language])
                excerpt = unescape(strip_tags(match["excerpt"]["rendered"])).strip()
                if content:
                    setattr(page, f"content_{language}", content)
                if excerpt:
                    setattr(page, f"excerpt_{language}", excerpt)
                    setattr(page, f"meta_description_{language}", excerpt[:500])
                if language == "en" and match.get("featured_media") and not page.featured_image:
                    self._import_featured_image(page, match["featured_media"], SOURCES[language], options["timeout"])
                updated += 1
            page.save()

        for source_page in fetched.get("en", []):
            source_slug = source_page.get("slug")
            page = Page.objects.filter(slug_en=source_slug).first()
            if not page:
                continue
            content = self._clean_content(source_page["content"]["rendered"], SOURCES["en"])
            if content:
                page.content_en = content
                page.save()

        self.stdout.write(self.style.SUCCESS(
            f"Site page import complete. Applied {updated} language-page matches."
        ))

    def _import_site_settings(self, base_url, timeout):
        try:
            response = requests.get(
                base_url,
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (compatible; REC-Django-Importer/1.0)"},
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            self.stdout.write(self.style.WARNING(f"Site settings source unavailable ({exc})"))
            return

        text = unescape(strip_tags(response.text))
        phones = []
        for phone in re.findall(r"\+250[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}", text):
            normalized = re.sub(r"\s+", " ", phone).strip()
            if normalized not in phones:
                phones.append(normalized)
        email_match = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)

        settings, _ = SiteSetting.objects.get_or_create(
            pk=1, defaults={"site_name": "The Ransom Evangelistic Centre"}
        )
        if phones:
            settings.phone_1 = phones[0]
            if len(phones) > 1:
                settings.phone_2 = phones[1]
            if len(phones) > 2:
                settings.phone_3 = phones[2]
        if email_match:
            settings.email = email_match.group(0)
            settings.contact_email = email_match.group(0)
        if "Kinyinya" in text:
            settings.address_line_1_en = "Kinyinya, KG 12 Avenue"
            settings.address_line_2_en = "Near Pottery Café Kigali"
        copyright_match = re.search(r"©\s*2024[^<\n]{0,100}All Rights Reserved\.?", text, re.I)
        if copyright_match:
            settings.copyright_text_en = re.sub(r"\s+", " ", copyright_match.group(0)).strip()
        settings.save()

    def _fetch_pages(self, base_url, timeout):
        endpoint = urljoin(
            base_url,
            "wp-json/wp/v2/pages?per_page=100&_fields=id,slug,link,title,content,excerpt,featured_media,parent,menu_order",
        )
        return self._get_json(endpoint, timeout)

    def _get_json(self, url, timeout):
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; REC-Django-Importer/1.0)",
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()

    def _match_page(self, spec, pages):
        aliases = {slug.lower() for slug in spec["source_slugs"]}
        aliases.add(spec["slug"]["en"].lower())
        exact_matches = [
            page for page in pages if page.get("slug", "").lower() in aliases
        ]
        if exact_matches:
            return max(
                exact_matches,
                key=lambda page: len(page.get("content", {}).get("rendered", "")),
            )

        if not spec["source_slugs"]:
            return None

        stopwords = {"a", "an", "and", "the", "of", "our", "to", "us", "we"}
        title_words = set(re.findall(r"[a-z]+", spec["title"]["en"].lower())) - stopwords
        best = None
        best_score = 0
        for page in pages:
            title = strip_tags(page.get("title", {}).get("rendered", "")).lower()
            words = set(re.findall(r"[a-z]+", title))
            score = len(title_words & words)
            if score > best_score:
                best, best_score = page, score
        return best if title_words and best_score >= max(1, len(title_words) // 2) else None

    def _clean_content(self, content, base_url):
        if not content:
            return ""
        content = re.sub(r"<script\b[^>]*>.*?</script>", "", content, flags=re.I | re.S)
        content = re.sub(r"<style\b[^>]*>.*?</style>", "", content, flags=re.I | re.S)
        def absolutize(match):
            attribute, quote, path = match.groups()
            return f" {attribute}={quote}{urljoin(base_url, path)}{quote}"

        content = re.sub(
            r"\s(src|href)=(['\"])(/[^'\"]*)\2",
            absolutize,
            content,
            flags=re.I,
        )
        return content.strip()

    def _import_featured_image(self, page, media_id, base_url, timeout):
        try:
            media = self._get_json(
                urljoin(base_url, f"wp-json/wp/v2/media/{media_id}?_fields=source_url,slug"),
                timeout,
            )
            image_url = media.get("source_url")
            if not image_url:
                return
            response = requests.get(
                image_url,
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (compatible; REC-Django-Importer/1.0)"},
            )
            response.raise_for_status()
            filename = image_url.rsplit("/", 1)[-1].split("?", 1)[0]
            page.featured_image.save(filename, ContentFile(response.content), save=False)
        except (requests.RequestException, json.JSONDecodeError):
            self.stdout.write(self.style.WARNING(f"Could not import image for {page.title_en}"))
