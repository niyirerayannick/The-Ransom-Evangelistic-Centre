from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.models import Q

from apps.core.models import MenuItem, SiteSetting
from apps.pages.models import Page
from apps.pages.site_defaults import PAGE_SPECS, PUBLICATION_SPECS


class Command(BaseCommand):
    help = "Seed multilingual institutional pages and dynamic menus."

    def handle(self, *args, **options):
        pages = {}
        for order, spec in enumerate(PAGE_SPECS):
            candidates = list(Page.objects.filter(
                Q(slug_en=spec["slug"]["en"])
                | Q(slug_fr=spec["slug"]["fr"])
                | Q(slug_rw=spec["slug"]["rw"])
            ))
            page = max(candidates, key=lambda item: len(item.content_en or ""), default=None)
            if page is None:
                page = Page()
            for duplicate in candidates:
                if duplicate.pk != page.pk:
                    duplicate.delete()
            page.title = spec["title"]["en"]
            page.slug = spec["slug"]["en"]
            page.content = page.content_en or spec["content"]["en"]
            page.excerpt = page.excerpt_en or spec["excerpt"]["en"]
            page.template_type = spec.get("template_type", "default")
            page.meta_title = spec["title"]["en"]
            page.meta_description = page.meta_description_en or spec["excerpt"]["en"]
            page.is_published = True
            page.is_active = True
            page.order = order
            for language in ("en", "fr", "rw"):
                setattr(page, f"title_{language}", spec["title"][language])
                setattr(page, f"slug_{language}", spec["slug"][language])
                if not spec["source_slugs"] or not getattr(page, f"content_{language}"):
                    setattr(page, f"content_{language}", spec["content"][language])
                if not spec["source_slugs"] or not getattr(page, f"excerpt_{language}"):
                    setattr(page, f"excerpt_{language}", spec["excerpt"][language])
                setattr(page, f"meta_title_{language}", spec["title"][language])
                if not getattr(page, f"meta_description_{language}"):
                    setattr(page, f"meta_description_{language}", spec["excerpt"][language])
            page.save()
            pages[spec["key"]] = page

        about_parent = pages.get("who-we-are")
        for child_key in ("our-history", "mission-and-vision", "leadership"):
            if pages.get(child_key):
                pages[child_key].parent = about_parent
                pages[child_key].save(update_fields=["parent"])

        for offset, (key, en, fr, rw) in enumerate(PUBLICATION_SPECS, start=len(pages)):
            page, _ = Page.objects.update_or_create(
                slug_en=key,
                defaults={
                    "title": en,
                    "slug": key,
                    "content": (
                        f"<p>Explore REC publications about {en.lower()}, written to offer "
                        "biblical wisdom, practical encouragement, and Gospel-centred reflection.</p>"
                    ),
                    "excerpt": f"REC publications and resources about {en.lower()}.",
                    "is_published": True,
                    "is_active": True,
                    "order": offset,
                },
            )
            translations = {"en": en, "fr": fr, "rw": rw}
            slugs = {
                "en": key,
                "fr": "livres" if key == "books" else key,
                "rw": "ibitabo" if key == "books" else key,
            }
            for language in ("en", "fr", "rw"):
                setattr(page, f"title_{language}", translations[language])
                setattr(page, f"slug_{language}", slugs[language])
            page.save()
            pages[key] = page

        settings, _ = SiteSetting.objects.get_or_create(
            pk=1, defaults={"site_name": "The Ransom Evangelistic Centre"}
        )
        settings.site_name_en = "The Ransom Evangelistic Centre"
        settings.site_name_fr = "Le Centre Évangélique de la Rançon"
        settings.site_name_rw = "The Ransom Evangelistic Centre"
        settings.email = settings.email or settings.contact_email or "info@gashugiyves.org"
        settings.contact_email = settings.contact_email or settings.email
        settings.phone_1 = settings.phone_1 or "+250 789 029 994"
        settings.phone_2 = settings.phone_2 or "+250 726 756 656"
        settings.phone_3 = settings.phone_3 or "+250 788 506 517"
        settings.address_line_1_en = settings.address_line_1_en or "Kinyinya, KG 12 Avenue"
        settings.address_line_1_fr = settings.address_line_1_fr or "Kinyinya, avenue KG 12"
        settings.address_line_1_rw = settings.address_line_1_rw or "Kinyinya, KG 12 Avenue"
        settings.address_line_2_en = settings.address_line_2_en or "Near Pottery Café Kigali"
        settings.address_line_2_fr = settings.address_line_2_fr or "Près de Pottery Café Kigali"
        settings.address_line_2_rw = settings.address_line_2_rw or "Hafi ya Pottery Café Kigali"
        settings.copyright_text = settings.copyright_text or "©2024. Yves Gashugi. All Rights Reserved."
        settings.save()

        self._seed_menus(pages)
        call_command("seed_ministry_content")
        self.stdout.write(self.style.SUCCESS("Multilingual pages and menus are ready."))

    def _menu(self, key, titles, order, pages, parent=None, location="main_menu", url=""):
        page = pages.get(key)
        item, _ = MenuItem.objects.update_or_create(
            location=location,
            parent=parent,
            title_en=titles["en"],
            defaults={
                "title": titles["en"],
                "page": page,
                "url": url,
                "order": order,
                "is_active": True,
            },
        )
        for language, title in titles.items():
            setattr(item, f"title_{language}", title)
        item.save()
        return item

    def _seed_menus(self, pages):
        home = self._menu(
            "home", {"en": "HOME", "fr": "ACCUEIL", "rw": "AHABANZA"}, 0, pages, url="/"
        )
        about = self._menu(
            "who-we-are", {"en": "ABOUT US", "fr": "À PROPOS", "rw": "ABO TURI BO"}, 1, pages
        )
        self._menu("who-we-are", {"en": "Who we are", "fr": "Qui sommes-nous", "rw": "Abo turi bo"}, 0, pages, about)
        self._menu("our-history", {"en": "Our History", "fr": "Notre histoire", "rw": "Amateka yacu"}, 1, pages, about)
        self._menu("mission-and-vision", {"en": "Mission and Vision", "fr": "Mission et vision", "rw": "Intego n’icyerekezo"}, 2, pages, about)
        self._menu("leadership", {"en": "Leadership", "fr": "Direction", "rw": "Ubuyobozi"}, 3, pages, about)

        self._menu("what-we-do", {"en": "WHAT WE DO", "fr": "CE QUE NOUS FAISONS", "rw": "IBYO DUKORA"}, 2, pages)
        publication = self._menu(
            "church", {"en": "PUBLICATION", "fr": "PUBLICATION", "rw": "INYANDIKO"}, 3, pages
        )
        publication.page = None
        publication.url = "/news/"
        publication.save()
        publication_children = [
            ("church", "Church", "Église", "Itorero", "/news/category/church/"),
            ("leadership", "Leadership", "Direction", "Ubuyobozi", "/news/category/leadership/"),
            ("family", "Family", "Famille", "Umuryango", "/news/category/family/"),
            (
                "constructive-criticism",
                "Constructive Criticism",
                "Critique constructive",
                "Ubusesenguzi",
                "/news/category/constructive-criticism/",
            ),
            ("healing", "Healing", "Guérison", "Isanamitima", "/news/category/healing/"),
            ("books", "Books", "Livres", "Ibitabo", ""),
        ]
        from apps.news.homepage import HOME_CATEGORY_SLUGS
        for order, (key, en, fr, rw, category_url) in enumerate(publication_children):
            item = self._menu(
                key,
                {"en": en, "fr": fr, "rw": rw},
                order,
                pages,
                publication,
                url=category_url,
            )
            if category_url:
                item.page = None
                item.url = category_url
                section = key if key in HOME_CATEGORY_SLUGS else None
                for language in ("en", "fr", "rw"):
                    if section:
                        slug = HOME_CATEGORY_SLUGS[section].get(language, HOME_CATEGORY_SLUGS[section]["en"])
                        setattr(item, f"url_{language}", f"/news/category/{slug}/")
                    else:
                        setattr(item, f"url_{language}", category_url)
                item.save()

        self._menu("find-a-counsellor", {"en": "FIND A COUNSELLOR", "fr": "TROUVER UN CONSEILLER", "rw": "SHAKA UMUJYANAMA"}, 4, pages)
        self._menu("contact-us", {"en": "CONTACT US", "fr": "CONTACTEZ-NOUS", "rw": "TWANDIKIRE"}, 5, pages)
        self._menu("donate", {"en": "DONATE", "fr": "FAIRE UN DON", "rw": "TANGA INKUNGA"}, 6, pages)

        footer_specs = [
            ("subscribe", {"en": "Subscribe to our Website", "fr": "S’abonner à notre site", "rw": "Iyandikishe ku rubuga"}, ""),
            ("website-policy", {"en": "Website Policy", "fr": "Politique du site", "rw": "Amabwiriza y’urubuga"}, ""),
            ("leave-a-comment", {"en": "Leave a comment", "fr": "Laisser un commentaire", "rw": "Tanga igitekerezo"}, ""),
        ]
        for order, (key, titles, url) in enumerate(footer_specs):
            self._menu(key, titles, order, pages, location="footer_quick_links", url=url)
