from django.core.management.base import BaseCommand

from apps.pages.donation_content import DONATION_METHODS, DONATION_PROGRAMS
from apps.pages.models import DonationMethod, DonationProgram, Page
from apps.pages.site_defaults import PAGE_SPECS


class Command(BaseCommand):
    help = "Seed donation programs, payment methods, and sync donate page copy."

    def handle(self, *args, **options):
        for item in DONATION_PROGRAMS:
            program, created = DonationProgram.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"]["en"],
                    "title_en": item["title"]["en"],
                    "title_fr": item["title"]["fr"],
                    "title_rw": item["title"]["rw"],
                    "description": item["description"]["en"],
                    "description_en": item["description"]["en"],
                    "description_fr": item["description"]["fr"],
                    "description_rw": item["description"]["rw"],
                    "icon": item["icon"],
                    "order": item["order"],
                    "is_active": True,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} program: {program.title}")

        for item in DONATION_METHODS:
            method, created = DonationMethod.objects.update_or_create(
                seed_key=item["key"],
                defaults={
                    "name": item["name"],
                    "name_en": item["name"],
                    "method_type": item["method_type"],
                    "bank_name": item.get("bank_name", ""),
                    "account_name": item.get("account_name", ""),
                    "account_number": item.get("account_number", ""),
                    "mobile_money_number": item.get("mobile_money_number", ""),
                    "currency": item.get("currency", "RWF"),
                    "icon": item.get("icon", ""),
                    "order": item["order"],
                    "is_active": True,
                    "instructions": item.get("instructions_en", ""),
                    "instructions_en": item.get("instructions_en", ""),
                    "instructions_fr": item.get("instructions_fr", ""),
                    "instructions_rw": item.get("instructions_rw", ""),
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} method: {method.name}")

        deactivated = DonationMethod.objects.filter(seed_key__isnull=True).update(is_active=False)
        if deactivated:
            self.stdout.write(f"Deactivated {deactivated} legacy payment method(s) without seed_key.")

        spec = next(item for item in PAGE_SPECS if item["key"] == "donate")
        page = (
            Page.objects.filter(slug_en=spec["slug"]["en"]).first()
            or Page.objects.filter(template_type="donate").first()
        )
        if page:
            page.template_type = "donate"
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
            self.stdout.write(self.style.SUCCESS(f"Synced donate page (pk={page.pk})"))

        self.stdout.write(self.style.SUCCESS("Donation data seeded successfully."))
