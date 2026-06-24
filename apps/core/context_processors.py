from django.db.models import Prefetch

from .models import MenuItem, SiteSetting


def site_settings(request):
    setting = SiteSetting.objects.first()
    return {"site_settings": setting}


def main_menu(request):
    active_children = MenuItem.objects.filter(is_active=True).order_by("order")
    menus = MenuItem.objects.filter(
        is_active=True, parent__isnull=True, location="main_menu"
    ).order_by("order").prefetch_related(Prefetch("children", queryset=active_children))
    topbar_items = MenuItem.objects.filter(
        is_active=True, parent__isnull=True, location="topbar"
    ).order_by("order")
    footer_links = MenuItem.objects.filter(
        is_active=True, parent__isnull=True, location="footer_quick_links"
    ).order_by("order")
    return {
        "main_menu": menus,
        "topbar_items": topbar_items,
        "footer_quick_links": footer_links,
    }
