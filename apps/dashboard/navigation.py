from django.urls import reverse, NoReverseMatch

from .roles import MODULES, user_can_access_module, user_can_manage_users


SIDEBAR_GROUPS = [
    ("main", "Main", [
        ("home", "Dashboard", "dashboard:home", "dashboard"),
        ("preview", "Website Preview", "home", "public", True),
    ]),
    ("content", "Content", [
        ("posts", "Posts", "dashboard:post_list", "article"),
        ("pages", "Pages", "dashboard:page_list", "description"),
        ("team", "Team / Leadership", "dashboard:team_list", "groups"),
        ("categories", "Categories", "dashboard:category_list", "category"),
        ("tags", "Tags", "dashboard:tag_list", "sell"),
        ("media", "Media Library", "dashboard:media_list", "perm_media"),
        ("comments", "Comments", "dashboard:comment_list", "chat"),
    ]),
    ("publishing", "Publishing", [
        ("books", "Books", "dashboard:book_list", "menu_book"),
        ("newsletter", "Newsletter", "dashboard:subscriber_list", "mail"),
    ]),
    ("engagement", "Engagement", [
        ("counselling", "Counselling Requests", "dashboard:counselling_requests", "support_agent"),
        ("counsellors", "Counsellors", "dashboard:counsellor_list", "psychology"),
        ("contact", "Contact Messages", "dashboard:contact_list", "contact_mail"),
        ("donations", "Donations", "dashboard:donation_list", "volunteer_activism"),
    ]),
    ("website", "Website Management", [
        ("menus", "Menus", "dashboard:menu_list", "menu"),
        ("ads", "Advertisements", "dashboard:ad_list", "campaign"),
        ("partners", "Partners", "dashboard:partner_list", "handshake"),
        ("homepage", "Homepage Sections", "dashboard:homepage_list", "home"),
        ("who_we_are_block", "Who We Are Block", "dashboard:who_we_are_edit", "info"),
        ("settings", "Site Settings", "dashboard:settings", "settings"),
    ]),
    ("administration", "Administration", [
        ("users", "Users", "dashboard:user_list", "group"),
        ("roles", "Roles & Permissions", "dashboard:roles", "admin_panel_settings"),
        ("audit", "Audit Logs", "dashboard:audit_logs", "history"),
        ("django_admin", "Django Admin", "admin:index", "build", True),
    ]),
]


def sidebar_navigation(user):
    items = []
    for group_key, group_label, links in SIDEBAR_GROUPS:
        group_items = []
        for link in links:
            module_key = link[0]
            if module_key == "preview":
                if user_can_access_module(user, "home"):
                    group_items.append(_nav_item(link, external=link[4] if len(link) > 4 else False))
                continue
            if module_key == "django_admin":
                if user.is_superuser:
                    group_items.append(_nav_item(link, external=False))
                continue
            if module_key in ("roles", "audit"):
                if user_can_manage_users(user) or user.is_superuser:
                    group_items.append(_nav_item(link))
                continue
            if module_key == "who_we_are_block":
                if user_can_access_module(user, "homepage"):
                    group_items.append(_nav_item(link))
                continue
            if module_key == "tags" and not user_can_access_module(user, "categories"):
                continue
            if not user_can_access_module(user, module_key):
                continue
            group_items.append(_nav_item(link))
        if group_items:
            items.append({"key": group_key, "label": group_label, "items": group_items})
    return items


def _nav_item(link, external=False):
    key, label, url_name, icon = link[:4]
    try:
        url = reverse(url_name) if not external or url_name != "home" else "/en/"
    except NoReverseMatch:
        url = "#"
    if external and url_name == "home":
        url = "/en/"
    return {"key": key, "label": label, "url": url, "icon": icon, "external": external}
