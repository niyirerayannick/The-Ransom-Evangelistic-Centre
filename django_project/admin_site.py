from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group


class RansomAdminSite(AdminSite):
    site_title = _("The Ransom Evangelistic Centre")
    site_header = _("The Ransom Evangelistic Centre - Admin")
    index_title = _("Dashboard")
    enable_nav_sidebar = True


admin_site = RansomAdminSite(name="ransom_admin")
admin.site.site_header = _("The Ransom Evangelistic Centre")
admin.site.site_title = _("TREC Admin")
admin.site.index_title = _("Dashboard")
