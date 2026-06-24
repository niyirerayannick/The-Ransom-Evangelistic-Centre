from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Book, BookCategory, ContactMessage, CounsellingRequest, Counsellor, DonationMethod,
    DonationPledge, DonationProgram, LeadershipMember, Page,
)
from apps.core.models import ImportSource


class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "template_type", "parent", "is_active", "show_in_menu", "order", "import_sources"]
    list_editable = ["is_active", "show_in_menu", "order"]
    list_filter = ["template_type", "is_active", "show_in_menu"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "content"]
    fieldsets = [
        (_("Content"), {"fields": ["title", "slug", "excerpt", "content", "featured_image"]}),
        (_("Structure"), {"fields": ["template_type", "parent", "order", "show_in_menu"]}),
        (_("SEO"), {"fields": ["meta_title", "seo_title", "meta_description"]}),
        (_("Publishing"), {"fields": ["is_published", "is_active"]}),
    ]

    def import_sources(self, obj):
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(obj)
        return ", ".join(
            f"{source.source_language}:{source.old_wordpress_id}"
            for source in ImportSource.objects.filter(content_type=content_type, object_id=obj.pk)
        )


admin.site.register(Page, PageAdmin)


@admin.register(LeadershipMember)
class LeadershipMemberAdmin(admin.ModelAdmin):
    list_display = ["photo_preview", "name", "role", "is_active", "order"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]
    search_fields = [
        "name", "name_en", "name_fr", "name_rw",
        "role", "role_en", "role_fr", "role_rw",
        "bio", "bio_en", "bio_fr", "bio_rw",
        "email", "phone",
    ]
    ordering = ["order", "name"]
    prepopulated_fields = {"slug": ("name_en",)}
    readonly_fields = ["created_at", "updated_at"]

    @admin.display(description=_("Photo"))
    def photo_preview(self, obj):
        from django.utils.html import format_html

        url = obj.photo_display_url()
        if not url:
            return "—"
        return format_html('<img src="{}" style="height:48px;width:48px;object-fit:cover;border-radius:9999px;" alt="">', url)


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "language", "price", "is_free", "is_featured", "is_active"]
    list_editable = ["is_free", "is_featured", "is_active"]
    list_filter = ["language", "category", "is_free", "is_featured", "is_active"]
    search_fields = ["title", "author", "description"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"


@admin.register(CounsellingRequest)
class CounsellingRequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "counselling_type", "preferred_language", "preferred_contact_method", "status", "created_at"]
    list_editable = ["status"]
    list_filter = ["status", "counselling_type", "preferred_language", "preferred_contact_method"]
    search_fields = ["full_name", "email", "phone", "message"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Counsellor)
class CounsellorAdmin(admin.ModelAdmin):
    list_display = ["photo_preview", "name", "role", "is_active", "order"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "name_en", "name_fr", "name_rw", "role", "role_en", "role_fr", "role_rw"]
    ordering = ["order", "name"]
    prepopulated_fields = {"slug": ("name_en",)}
    readonly_fields = ["created_at", "updated_at"]

    @admin.display(description=_("Photo"))
    def photo_preview(self, obj):
        from django.utils.html import format_html

        url = obj.photo_display_url()
        if not url:
            return "—"
        return format_html('<img src="{}" style="height:48px;width:48px;object-fit:cover;border-radius:9999px;" alt="">', url)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["full_name", "subject", "email", "status", "created_at"]
    list_editable = ["status"]
    list_filter = ["status", "created_at"]
    search_fields = ["full_name", "email", "phone", "subject", "message"]
    readonly_fields = ["created_at"]


@admin.register(DonationMethod)
class DonationMethodAdmin(admin.ModelAdmin):
    list_display = ["name", "method_type", "currency", "account_number", "mobile_money_number", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["method_type", "is_active"]
    search_fields = ["name", "name_en", "account_number", "mobile_money_number", "bank_name"]
    ordering = ["order", "name"]


@admin.register(DonationProgram)
class DonationProgramAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["title", "title_en", "title_fr", "title_rw", "slug"]
    prepopulated_fields = {"slug": ("title_en",)}
    ordering = ["order", "title"]


@admin.register(DonationPledge)
class DonationPledgeAdmin(admin.ModelAdmin):
    list_display = [
        "full_name", "program_to_donate", "amount", "currency",
        "payment_gateway", "donation_commitment", "status", "created_at",
    ]
    list_editable = ["status"]
    list_filter = ["status", "program_to_donate", "payment_gateway", "donation_commitment", "created_at"]
    search_fields = ["full_name", "email", "telephone", "feedback"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
