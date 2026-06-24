from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.core.models import Advertisement, HomepageSection, Menu, Partner, SiteSetting
from apps.news.models import Category


def svg_file(label, width, height, background="#f4f1e8", foreground="#0b5f89"):
    safe_label = label.replace("&", "and").replace("<", "").replace(">", "")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="100%" height="100%" fill="{background}"/>
    <circle cx="{width * .18}" cy="{height * .5}" r="{min(width, height) * .22}" fill="#d39200" opacity=".2"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{foreground}" font-family="Georgia,serif" font-size="{max(16, min(width, height) // 6)}" font-weight="700">{safe_label}</text>
    </svg>"""
    return ContentFile(svg.encode("utf-8"))


class Command(BaseCommand):
    help = "Create default menus, homepage content, advertisements, and partners (no demo articles)."

    def handle(self, *args, **options):
        site, _ = SiteSetting.objects.get_or_create(
            pk=1,
            defaults={
                "site_name": "The Ransom Evangelistic Centre",
                "tagline": "Wisdom. Salvation. Empower.",
                "contact_email": "info@gashugiyves.org",
                "contact_phone": "+250 789 029 994",
                "phone_1": "+250 789 029 994",
                "phone_2": "+250 726 756 656",
                "phone_3": "+250 788 506 517",
                "address_line_1": "Kinyinya, KG 12 Avenue",
                "address_line_2": "Near Pottery Cafe Kigali",
                "copyright_text": "©2024. Yves Gashugi. All Rights Reserved.",
            },
        )
        if not site.phone_1:
            site.phone_1 = "+250 789 029 994"
            site.phone_2 = "+250 726 756 656"
            site.phone_3 = "+250 788 506 517"
            site.address_line_1 = "Kinyinya, KG 12 Avenue"
            site.address_line_2 = "Near Pottery Cafe Kigali"
            site.copyright_text = "©2024. Yves Gashugi. All Rights Reserved."
            site.save()

        menu_data = [
            ("HOME", "/", []),
            ("ABOUT US", "/page/who-we-are/", [
                ("Who we are", "/page/who-we-are/"),
                ("Our History", "/page/our-history/"),
                ("Mission and Vision", "/page/mission-and-vision/"),
                ("Leadership", "/news/category/leadership/"),
            ]),
            ("WHAT WE DO", "/page/what-we-do/", []),
            ("PUBLICATION", "/news/", [
                ("Church", "/news/category/church/"),
                ("Leadership", "/news/category/leadership/"),
                ("Family", "/news/category/family/"),
                ("Constructive Criticism", "/news/category/constructive-criticism/"),
                ("Healing", "/news/category/healing/"),
                ("Books", "/news/category/books/"),
            ]),
            ("FIND A COUNSELLOR", "/page/find-a-counsellor/", []),
            ("CONTACT US", "/page/contact-us/", []),
            ("DONATE", "/page/donate/", []),
        ]
        for order, (title, url, children) in enumerate(menu_data):
            parent, _ = Menu.objects.update_or_create(
                title=title, parent=None, defaults={"url": url, "order": order, "is_active": True}
            )
            for child_order, (child_title, child_url) in enumerate(children):
                Menu.objects.update_or_create(
                    title=child_title,
                    parent=parent,
                    defaults={"url": child_url, "order": child_order, "is_active": True},
                )

        HomepageSection.objects.update_or_create(
            key="who-we-are",
            defaults={
                "title": "THE RANSOM EVANGELISTIC CENTRE Abbreviated as “REC”",
                "section_type": "featured",
                "content": (
                    "<p>Founded in 2023, REC exists to inform the Gospel of Jesus Christ in all lens "
                    "with the aim of equipping the church and helping believers and unbelievers believe "
                    "with true wisdom through articles writing and every other effective means that bring salvation.</p>"
                ),
                "button_text": "FIND A COUNSELLOR",
                "button_url": "find-a-counsellor",
                "is_active": True,
            },
        )
        from apps.core.homepage_content import sync_who_we_are_section
        sync_who_we_are_section()

        category_names = ["Church", "Leadership", "Family", "Constructive Criticism", "Healing", "Books"]
        for ordering, name in enumerate(category_names):
            slug = slugify(name)
            Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "ordering": ordering, "order": ordering, "is_active": True},
            )

        if not Advertisement.objects.filter(position="home_after_featured").exists():
            ad = Advertisement(
                title="REC Community Advertisement",
                position="home_after_featured",
                link="https://yvesgashugi.org/",
                desktop_width=970,
                desktop_height=90,
                mobile_width=320,
                mobile_height=100,
            )
            ad.image.save("rec-community-ad.svg", svg_file("REC • Wisdom • Salvation • Empower", 970, 90), save=False)
            ad.mobile_image.save("rec-community-ad-mobile.svg", svg_file("REC Community", 320, 100), save=False)
            ad.save()

        partner_names = ["Bravetech", "Nkunda Gospel", "Christian Family", "Geruka Healing Centre", "Dive in the Truth"]
        for ordering, name in enumerate(partner_names):
            partner, created = Partner.objects.get_or_create(
                name=name, defaults={"ordering": ordering, "is_active": True}
            )
            if created or not partner.logo:
                partner.logo.save(
                    f"{slugify(name)}.svg",
                    svg_file(name, 260, 150, "#ffffff", "#0b5f89"),
                    save=True,
                )

        self.stdout.write(self.style.SUCCESS("Homepage seed data is ready."))
