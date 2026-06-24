from django.core.management.base import BaseCommand
from django.test import Client
from django.utils import translation

from apps.core.models import MenuItem
from apps.news.homepage import posts_for_language, post_has_language_content, DEMO_CONTENT_MARKER


class Command(BaseCommand):
    help = "Verify multilingual homepage, menus, and category URLs."

    def handle(self, *args, **options):
        client = Client(HTTP_HOST="127.0.0.1")
        errors = []

        self.stdout.write("Language counts:")
        for lang in ("en", "fr", "rw"):
            self.stdout.write(f"  {lang}: {posts_for_language(lang).count()}")

        for lang in ("en", "fr", "rw"):
            with translation.override(lang):
                response = client.get(f"/{lang}/")
                if response.status_code != 200:
                    errors.append(f"{lang} homepage status {response.status_code}")

        for path in (
            "/en/news/category/church/",
            "/fr/news/category/itorero/",
            "/rw/news/category/itorero/",
            "/rw/news/category/ubuyobozi/",
            "/en/search/?q=church",
        ):
            response = client.get(path)
            if response.status_code not in (200, 404):
                errors.append(f"{path} returned {response.status_code}")

        if posts_for_language("en").filter(content__icontains=DEMO_CONTENT_MARKER).exists():
            errors.append("Demo posts found in English listings")

        self.stdout.write("\nMenu sample (fr):")
        with translation.override("fr"):
            for item in MenuItem.objects.filter(location="main_menu", parent__isnull=True).order_by("order")[:4]:
                self.stdout.write(f"  {item.title} -> {item.get_url()}")

        if errors:
            self.stdout.write(self.style.ERROR("\nIssues:"))
            for err in errors:
                self.stdout.write(f"  - {err}")
        else:
            self.stdout.write(self.style.SUCCESS("\nAll QA checks passed."))
