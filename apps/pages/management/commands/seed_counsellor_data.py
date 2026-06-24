from django.core.management.base import BaseCommand

from apps.pages.counselling_content import COUNSELLOR_SEED, CONTACT_INFO
from apps.pages.models import Counsellor, Page
from apps.pages.site_defaults import PAGE_SPECS


class Command(BaseCommand):
    help = "Seed counsellor profile and sync find-a-counsellor page copy."

    def handle(self, *args, **options):
        seed = COUNSELLOR_SEED
        counsellor, created = Counsellor.objects.update_or_create(
            seed_key=seed["seed_key"],
            defaults={
                "name": seed["name"]["en"],
                "name_en": seed["name"]["en"],
                "name_fr": seed["name"]["fr"],
                "name_rw": seed["name"]["rw"],
                "slug": seed["slug"],
                "role": seed["role"]["en"],
                "role_en": seed["role"]["en"],
                "role_fr": seed["role"]["fr"],
                "role_rw": seed["role"]["rw"],
                "bio": seed["bio"]["en"],
                "bio_en": seed["bio"]["en"],
                "bio_fr": seed["bio"]["fr"],
                "bio_rw": seed["bio"]["rw"],
                "phone": seed["phone"],
                "email": seed["email"] or CONTACT_INFO["email"],
                "order": 0,
                "is_active": True,
            },
        )
        action = "Created" if created else "Updated"
        self.stdout.write(f"{action} counsellor: {counsellor.name}")

        spec = next(item for item in PAGE_SPECS if item["key"] == "find-a-counsellor")
        page = (
            Page.objects.filter(slug_en=spec["slug"]["en"]).first()
            or Page.objects.filter(template_type="find_counsellor").first()
        )
        if page:
            page.template_type = "find_counsellor"
            page.is_published = True
            page.is_active = True
            for lang in ("en", "fr", "rw"):
                setattr(page, f"title_{lang}", spec["title"][lang])
                setattr(page, f"slug_{lang}", spec["slug"][lang])
                setattr(page, f"excerpt_{lang}", spec["excerpt"][lang])
                setattr(page, f"content_{lang}", spec["content"][lang])
            page.title = spec["title"]["en"]
            page.slug = spec["slug"]["en"]
            page.excerpt = spec["excerpt"]["en"]
            page.content = spec["content"]["en"]
            page.save()
            self.stdout.write(self.style.SUCCESS(f"Synced find-a-counsellor page (pk={page.pk})"))

        self.stdout.write(self.style.SUCCESS("Counsellor data seeded successfully."))
