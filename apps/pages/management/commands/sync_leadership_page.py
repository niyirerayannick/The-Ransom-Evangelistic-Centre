from django.core.management.base import BaseCommand

from apps.pages.models import Page
from apps.pages.site_defaults import PAGE_SPECS


class Command(BaseCommand):
    help = "Sync Leadership page copy (EN/FR/RW) and template from site defaults."

    def handle(self, *args, **options):
        spec = next(item for item in PAGE_SPECS if item["key"] == "leadership")
        page = (
            Page.objects.filter(slug_en=spec["slug"]["en"]).first()
            or Page.objects.filter(slug_fr=spec["slug"]["fr"]).first()
            or Page.objects.filter(slug_rw=spec["slug"]["rw"]).first()
        )
        if not page:
            self.stderr.write(self.style.ERROR("Leadership page not found."))
            return

        page.template_type = "leadership"
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

        self.stdout.write(self.style.SUCCESS(
            f"Synced leadership page (pk={page.pk}): /en/leadership/, /fr/direction/, /rw/ubuyobozi/"
        ))
