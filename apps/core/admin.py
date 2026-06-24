from django.contrib import admin
from .models import (
    Advertisement, HomepageSection, ImportSource, MediaAsset, Menu, MenuItem,
    Partner, Redirect, SiteSetting, Slider,
)


class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ["site_name", "contact_email", "updated_at"]
    fieldsets = [
        ("General", {"fields": ["site_name", "tagline", "logo", "footer_logo", "favicon", "default_language"]}),
        ("Footer", {"fields": ["footer_text", "copyright_text"]}),
        ("Social Media", {"fields": ["facebook_url", "twitter_url", "x_url", "instagram_url", "youtube_url"]}),
        ("Contact", {"fields": ["contact_email", "email", "contact_phone", "phone_1", "phone_2", "phone_3", "address", "address_line_1", "address_line_2"]}),
        ("Analytics", {"fields": ["google_analytics_id"]}),
    ]


class MenuAdmin(admin.ModelAdmin):
    list_display = ["title", "url", "page", "parent", "order", "is_active", "open_in_new_tab"]
    list_editable = ["order", "is_active", "open_in_new_tab"]
    list_filter = ["is_active"]
    search_fields = ["title"]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["title", "location", "page", "parent", "order", "is_active", "open_in_new_tab"]
    list_editable = ["order", "is_active", "open_in_new_tab"]
    list_filter = ["location", "is_active"]
    search_fields = ["title", "url"]
    autocomplete_fields = ["page", "parent"]


class HomepageSectionAdmin(admin.ModelAdmin):
    list_display = ["title", "key", "section_type", "category", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["section_type", "is_active"]


class SliderAdmin(admin.ModelAdmin):
    list_display = ["title", "order", "is_active", "post"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ["title", "position", "is_active", "start_date", "end_date", "clicks"]
    list_editable = ["is_active"]
    list_filter = ["position", "is_active"]
    search_fields = ["title"]


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ["name", "ordering", "is_active", "website_url"]
    list_editable = ["ordering", "is_active"]
    search_fields = ["name"]


admin.site.register(SiteSetting, SiteSettingAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(HomepageSection, HomepageSectionAdmin)
admin.site.register(Slider, SliderAdmin)


@admin.register(ImportSource)
class ImportSourceAdmin(admin.ModelAdmin):
    list_display = ["source_database", "source_language", "source_type", "old_wordpress_id", "content_type", "object_id", "import_status", "imported_at"]
    list_filter = ["source_database", "source_language", "source_type", "import_status"]
    search_fields = ["old_url", "old_wordpress_id"]
    readonly_fields = ["imported_at"]


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ["old_url", "new_url", "source_language", "content_type_name", "is_active"]
    list_editable = ["is_active"]
    list_filter = ["source_language", "content_type_name", "is_active"]
    search_fields = ["old_url", "new_url"]


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ["title", "source_language", "mime_type", "old_wordpress_id", "is_missing", "uploaded_at"]
    list_filter = ["source_language", "mime_type", "is_missing"]
    search_fields = ["title", "alt_text", "old_file_path", "remote_url"]
    readonly_fields = ["imported_at"]
