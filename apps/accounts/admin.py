from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "is_staff", "is_active", "wordpress_source", "wordpress_user_id", "imported_at"]
    list_filter = ["role", "is_staff", "is_active", "wordpress_source"]
    fieldsets = BaseUserAdmin.fieldsets + (
        (_("Profile"), {"fields": ("role", "bio", "profile_image", "phone", "website")}),
        (_("Social"), {"fields": ("facebook_profile", "twitter_profile")}),
        (_("WordPress import"), {"fields": ("wordpress_source", "wordpress_user_id", "imported_at")}),
    )
    readonly_fields = ["imported_at"]
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_("Profile"), {"fields": ("role",)}),
    )


admin.site.register(User, UserAdmin)
