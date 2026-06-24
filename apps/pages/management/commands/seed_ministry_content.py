from datetime import date

from django.core.management.base import BaseCommand

from apps.pages.models import Book, BookCategory, DonationMethod, LeadershipMember, Page


class Command(BaseCommand):
    help = "Seed editable content for the redesigned ministry pages."

    def handle(self, *args, **options):
        template_map = {
            "who-we-are": "who_we_are",
            "our-history": "our_history",
            "mission-and-vision": "mission_and_vision",
            "leadership": "leadership",
            "what-we-do": "what_we_do",
            "books": "books",
            "find-a-counsellor": "find_counsellor",
            "contact-us": "contact",
            "donate": "donate",
        }
        for slug, template_type in template_map.items():
            Page.objects.filter(slug_en=slug).update(template_type=template_type)

        leader, _ = LeadershipMember.objects.update_or_create(
            name="Yves Gashugi",
            defaults={
                "role": "Founder and Lead Minister",
                "role_fr": "Fondateur et responsable du ministère",
                "role_rw": "Uwashinze REC n’umuyobozi w’umurimo",
                "bio": (
                    "<p>Yves Gashugi serves REC through Christian writing, biblical teaching, "
                    "counselling ministry, and a commitment to helping people encounter wisdom "
                    "and salvation in Jesus Christ.</p>"
                ),
                "bio_fr": (
                    "<p>Yves Gashugi sert REC par l’écriture chrétienne, l’enseignement biblique, "
                    "l’accompagnement et le désir d’aider chacun à trouver la sagesse et le salut "
                    "en Jésus-Christ.</p>"
                ),
                "bio_rw": (
                    "<p>Yves Gashugi akorera REC binyuze mu nyandiko za Gikristo, inyigisho za "
                    "Bibiliya n’ubujyanama, agamije gufasha abantu kubona ubwenge n’agakiza muri Yesu Kristo.</p>"
                ),
                "email": "info@gashugiyves.org",
                "order": 0,
                "is_featured": True,
                "is_active": True,
            },
        )
        LeadershipMember.objects.update_or_create(
            name="REC Editorial Team",
            defaults={
                "role": "Publication and Teaching",
                "role_fr": "Publications et enseignement",
                "role_rw": "Inyandiko n’inyigisho",
                "bio": "<p>The editorial team prepares Gospel-centred articles, books, and teaching resources.</p>",
                "order": 1,
                "is_active": True,
            },
        )
        LeadershipMember.objects.update_or_create(
            name="REC Care Team",
            defaults={
                "role": "Counselling and Community Care",
                "role_fr": "Accompagnement et service communautaire",
                "role_rw": "Ubujyanama no kwita ku muryango",
                "bio": "<p>The care team helps connect people with compassionate listening, prayer, and guidance.</p>",
                "order": 2,
                "is_active": True,
            },
        )

        categories = {}
        category_specs = [
            ("christian-living", "Christian Living", "Vie chrétienne", "Imibereho ya Gikristo"),
            ("healing-family", "Healing and Family", "Guérison et famille", "Isanamitima n’umuryango"),
            ("leadership", "Leadership", "Direction", "Ubuyobozi"),
        ]
        for slug, en, fr, rw in category_specs:
            category, _ = BookCategory.objects.update_or_create(
                slug=slug,
                defaults={"name": en, "name_fr": fr, "name_rw": rw, "is_active": True},
            )
            categories[slug] = category

        books = [
            ("wisdom-for-the-journey", "Wisdom for the Journey", "Christian Living", "A practical Gospel-centred guide for growing in discernment and faithful living.", "en", True),
            ("healing-the-heart", "Healing the Heart", "Healing and Family", "Reflections for people seeking hope, restoration, and a healthier inner life.", "en", False),
            ("constructive-leadership", "Constructive Leadership", "Leadership", "Biblical principles for serving people with truth, courage, and humility.", "en", False),
            ("letters-to-the-church", "Letters to the Church", "Christian Living", "A collection of pastoral reflections written to strengthen the church.", "multi", False),
        ]
        category_by_name = {category.name: category for category in categories.values()}
        for index, (slug, title, category_name, description, language, featured) in enumerate(books):
            Book.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "author": "Yves Gashugi",
                    "description": f"<p>{description}</p>",
                    "language": language,
                    "category": category_by_name[category_name],
                    "is_free": True,
                    "published_at": date(2026, 1, index + 1),
                    "is_featured": featured,
                    "is_active": True,
                },
            )

        DonationMethod.objects.update_or_create(
            name="MTN Mobile Money",
            defaults={
                "method_type": "mobile_money",
                "account_name": "The Ransom Evangelistic Centre",
                "mobile_money_number": "+250 789 029 994",
                "instructions": "Use the REC contact number and include your name in the payment reference.",
                "order": 0,
                "is_active": True,
            },
        )
        DonationMethod.objects.update_or_create(
            name="Bank Transfer",
            defaults={
                "method_type": "bank",
                "account_name": "The Ransom Evangelistic Centre",
                "instructions": "Contact REC for current bank account details and transfer guidance.",
                "order": 1,
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Redesigned ministry page content is ready."))
