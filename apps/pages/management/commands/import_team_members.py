import os
import re
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.html import linebreaks

from apps.pages.models import LeadershipMember
from apps.pages.team_scraper import OUR_TEAM_URL, fetch_team_page_html, parse_team_members, slug_from_name


class Command(BaseCommand):
    help = "Import leadership team members from the legacy WordPress our-team page."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default=OUR_TEAM_URL,
            help="Source URL for the legacy team page.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and display results without saving to the database.",
        )
        parser.add_argument(
            "--force-images",
            action="store_true",
            help="Re-download images even when a photo already exists.",
        )
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Do not download images; store external URLs only.",
        )

    def handle(self, *args, **options):
        url = options["url"]
        self.stdout.write(f"Fetching team data from {url}")
        html = fetch_team_page_html(url)
        members = parse_team_members(html)
        if not members:
            self.stderr.write(self.style.ERROR("No team members found on the source page."))
            return

        created = updated = 0
        image_ok = image_failed = 0

        for item in members:
            if options["dry_run"]:
                self.stdout.write(
                    f"- {item['name']} | {item['role']} | photo={'yes' if item['photo_url'] else 'no'} | bio={len(item['bio'])} chars"
                )
                continue

            bio_html = linebreaks(item["bio"]) if item["bio"] else ""
            defaults = {
                "name": item["name"],
                "name_en": item["name"],
                "role": item["role"],
                "role_en": item["role"],
                "bio": bio_html,
                "bio_en": bio_html,
                "email": item["email"],
                "phone": item["phone"],
                "facebook_url": item["facebook_url"],
                "x_url": item["x_url"],
                "instagram_url": item["instagram_url"],
                "linkedin_url": item["linkedin_url"],
                "external_photo_url": item["photo_url"],
                "order": item["order"],
                "is_active": True,
            }
            member, was_created = LeadershipMember.objects.update_or_create(
                slug=item["slug"],
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

            if item["photo_url"] and not options["skip_images"]:
                if member.photo and not options["force_images"]:
                    self.stdout.write(f"  Photo kept for {member.name}")
                else:
                    ok = self._download_photo(member, item["photo_url"])
                    if ok:
                        image_ok += 1
                    else:
                        image_failed += 1
                        self.stdout.write(self.style.WARNING(f"  Image download failed for {member.name}"))

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Dry run complete. Parsed {len(members)} members."))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Imported {len(members)} team members ({created} created, {updated} updated). "
            f"Images downloaded: {image_ok}, failed: {image_failed}."
        ))

    def _download_photo(self, member, url):
        try:
            response = requests.get(
                url,
                timeout=45,
                headers={"User-Agent": "Mozilla/5.0 (compatible; RECSiteImporter/1.0)"},
            )
            response.raise_for_status()
            filename = os.path.basename(urlparse(url).path) or f"{member.slug}.jpg"
            filename = re.sub(r"[^A-Za-z0-9._-]", "-", filename)
            member.photo.save(filename, ContentFile(response.content), save=True)
            return True
        except Exception as exc:
            member.external_photo_url = url
            member.save(update_fields=["external_photo_url"])
            self.stderr.write(self.style.WARNING(f"  {member.name}: {exc}"))
            return False
