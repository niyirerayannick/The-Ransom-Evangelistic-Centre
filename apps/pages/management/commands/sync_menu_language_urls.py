from django.core.management.base import BaseCommand

from apps.core.models import MenuItem
from apps.news.homepage import HOME_CATEGORY_SLUGS


MENU_CATEGORY_KEYS = {
    "church": "church",
    "leadership": "leadership",
    "family": "family",
    "constructive-criticism": "constructive-criticism",
    "healing": "healing",
}


class Command(BaseCommand):
    help = "Sync publication submenu URLs to language-specific category slugs."

    def handle(self, *args, **options):
        updated = 0
        for item in MenuItem.objects.filter(url__contains="/news/category/"):
            section = None
            for key in MENU_CATEGORY_KEYS:
                if key in (item.url or ""):
                    section = key
                    break
            if not section:
                continue
            slug_map = HOME_CATEGORY_SLUGS[section]
            item.url = f"/news/category/{slug_map['en']}/"
            for language in ("en", "fr", "rw"):
                slug = slug_map.get(language) or slug_map["en"]
                setattr(item, f"url_{language}", f"/news/category/{slug}/")
            item.save()
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} menu item(s)."))
