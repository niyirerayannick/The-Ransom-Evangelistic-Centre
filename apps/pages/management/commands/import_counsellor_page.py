from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.pages.counselling_content import COUNSELLOR_SEED, CONTACT_INFO
from apps.pages.counsellor_scraper import FIND_COUNSELLOR_URL, fetch_page_html, parse_counsellor_page
from apps.pages.models import Counsellor
from apps.pages.site_defaults import PAGE_SPECS


class Command(BaseCommand):
    help = "Import counsellor photo and profile details from the legacy WordPress page."

    def add_arguments(self, parser):
        parser.add_argument("--url", default=FIND_COUNSELLOR_URL)

    def handle(self, *args, **options):
        html = fetch_page_html(options["url"])
        parsed = parse_counsellor_page(html)
        seed = COUNSELLOR_SEED
        counsellor, created = Counsellor.objects.update_or_create(
            seed_key=seed["seed_key"],
            defaults={
                "name": parsed["name"] or seed["name"]["en"],
                "name_en": parsed["name"] or seed["name"]["en"],
                "role": parsed["role"] or seed["role"]["en"],
                "role_en": parsed["role"] or seed["role"]["en"],
                "bio": parsed["bio"] or seed["bio"]["en"],
                "bio_en": parsed["bio"] or seed["bio"]["en"],
                "phone": seed["phone"],
                "email": seed["email"] or CONTACT_INFO["email"],
                "slug": seed["slug"],
                "order": 0,
                "is_active": True,
            },
        )
        if parsed.get("photo_url") and not counsellor.photo:
            try:
                import requests

                response = requests.get(parsed["photo_url"], timeout=30)
                response.raise_for_status()
                filename = f"{slugify(counsellor.slug or 'counsellor')}.jpg"
                counsellor.photo.save(filename, ContentFile(response.content), save=False)
                counsellor.external_photo_url = parsed["photo_url"]
                counsellor.save()
                self.stdout.write(self.style.SUCCESS(f"Downloaded photo for {counsellor.name}"))
            except Exception as exc:
                counsellor.external_photo_url = parsed["photo_url"]
                counsellor.save(update_fields=["external_photo_url"])
                self.stdout.write(self.style.WARNING(f"Saved external photo URL only: {exc}"))
        elif parsed.get("photo_url"):
            counsellor.external_photo_url = parsed["photo_url"]
            counsellor.save(update_fields=["external_photo_url"])

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} counsellor: {counsellor.name}"))
