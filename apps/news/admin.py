from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Category, Tag, Post, PostView, MediaLibrary
from apps.core.models import ImportSource


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "order", "post_count", "import_sources"]
    list_editable = ["is_active", "order"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = _("Posts")

    def import_sources(self, obj):
        return self._sources(obj)

    def _sources(self, obj):
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(obj)
        return ", ".join(
            f"{source.source_language}:{source.old_wordpress_id}"
            for source in ImportSource.objects.filter(content_type=content_type, object_id=obj.pk)
        )


class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class LanguageCompletionFilter(admin.SimpleListFilter):
    title = _("Language completion")
    parameter_name = "lang_complete"

    def lookups(self, request, model_admin):
        return [
            ("en_complete", _("English complete")),
            ("en_missing", _("English missing")),
            ("fr_complete", _("French complete")),
            ("fr_missing", _("French missing")),
            ("rw_complete", _("Kinyarwanda complete")),
            ("rw_missing", _("Kinyarwanda missing")),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "en_complete":
            return queryset.filter(Q(english_complete=True) | Q(title_en__gt="", content_en__gt=""))
        if value == "en_missing":
            return queryset.filter(Q(title_en="") | Q(title_en__isnull=True) | Q(content_en="") | Q(content_en__isnull=True))
        if value == "fr_complete":
            return queryset.filter(Q(french_complete=True) | Q(title_fr__gt="", content_fr__gt=""))
        if value == "fr_missing":
            return queryset.filter(Q(title_fr="") | Q(title_fr__isnull=True) | Q(content_fr="") | Q(content_fr__isnull=True))
        if value == "rw_complete":
            return queryset.filter(Q(kinyarwanda_complete=True) | Q(title_rw__gt="", content_rw__gt=""))
        if value == "rw_missing":
            return queryset.filter(Q(title_rw="") | Q(title_rw__isnull=True) | Q(content_rw="") | Q(content_rw__isnull=True))
        return queryset


class HasLanguageFilter(admin.SimpleListFilter):
    title = _("Has language")
    parameter_name = "has_language"

    def lookups(self, request, model_admin):
        return [
            ("has_en", _("Has English")),
            ("has_fr", _("Has French")),
            ("has_rw", _("Has Kinyarwanda")),
            ("missing_en", _("Missing English")),
            ("missing_fr", _("Missing French")),
            ("missing_rw", _("Missing Kinyarwanda")),
        ]

    def queryset(self, request, queryset):
        from .homepage import post_available_in_language_q

        value = self.value()
        if value == "has_en":
            return queryset.filter(post_available_in_language_q("en"))
        if value == "has_fr":
            return queryset.filter(post_available_in_language_q("fr"))
        if value == "has_rw":
            return queryset.filter(post_available_in_language_q("rw"))
        if value == "missing_en":
            return queryset.exclude(post_available_in_language_q("en"))
        if value == "missing_fr":
            return queryset.exclude(post_available_in_language_q("fr"))
        if value == "missing_rw":
            return queryset.exclude(post_available_in_language_q("rw"))
        return queryset


class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title_en_display", "status", "category", "author", "language_summary",
        "is_featured", "views_count", "published_at", "import_sources",
    ]
    list_filter = [
        "status", "source_language", "is_featured", "is_breaking", "category", "author",
        HasLanguageFilter, LanguageCompletionFilter, "published_at",
    ]
    search_fields = [
        "title_en", "title_fr", "title_rw",
        "content_en", "content_fr", "content_rw",
        "excerpt_en", "excerpt_fr", "excerpt_rw",
    ]
    date_hierarchy = "published_at"
    raw_id_fields = ["author", "category", "reviewed_by"]
    filter_horizontal = ["tags"]
    readonly_fields = ["reviewed_at", "created_at", "updated_at", "reading_time", "views_count"]
    fieldsets = [
        (_("English"), {"fields": [
            "title_en", "slug_en", "excerpt_en", "content_en", "seo_title_en", "meta_description_en", "english_complete",
        ]}),
        (_("French"), {"fields": [
            "title_fr", "slug_fr", "excerpt_fr", "content_fr", "seo_title_fr", "meta_description_fr", "french_complete",
        ]}),
        (_("Kinyarwanda"), {"fields": [
            "title_rw", "slug_rw", "excerpt_rw", "content_rw", "seo_title_rw", "meta_description_rw", "kinyarwanda_complete",
        ]}),
        (_("Media & Taxonomy"), {"fields": ["featured_image", "category", "tags"]}),
        (_("Author & Status"), {"fields": [
            "author", "status", "source_language", "is_featured", "is_breaking", "allow_comments",
        ]}),
        (_("Publishing"), {"fields": ["published_at", "scheduled_at"]}),
        (_("Review"), {"fields": ["reviewed_by", "reviewed_at", "rejection_reason"]}),
        (_("Legacy base fields"), {"classes": ("collapse",), "fields": ["title", "slug", "excerpt", "content", "seo_title", "meta_description"]}),
        (_("Stats"), {"classes": ("collapse",), "fields": ["reading_time", "views_count", "created_at", "updated_at"]}),
    ]

    def title_en_display(self, obj):
        return obj.title_en or obj.title
    title_en_display.short_description = _("Title (EN)")

    def language_summary(self, obj):
        from django.utils.safestring import mark_safe
        badges = []
        for lang, label in (("en", "EN"), ("fr", "FR"), ("rw", "RW")):
            status = obj.translation_status().get(lang, {})
            color = "#16a34a" if status.get("complete") else "#dc2626"
            badges.append(f'<span style="color:{color}">{label}</span>')
        return mark_safe(" / ".join(badges))
    language_summary.short_description = _("Languages")

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        if obj.title_en:
            obj.title = obj.title_en
        if obj.slug_en:
            obj.slug = obj.slug_en
        if obj.content_en:
            obj.content = obj.content_en
        super().save_model(request, obj, form, change)

    def import_sources(self, obj):
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(obj)
        return ", ".join(
            f"{source.source_language}:{source.old_wordpress_id}"
            for source in ImportSource.objects.filter(content_type=content_type, object_id=obj.pk)
        )


class MediaLibraryAdmin(admin.ModelAdmin):
    list_display = ["title", "file_type", "uploaded_by", "created_at"]
    list_filter = ["file_type", "created_at"]
    search_fields = ["title", "alt_text", "caption"]
    raw_id_fields = ["uploaded_by"]


class PostViewAdmin(admin.ModelAdmin):
    list_display = ["post", "ip_address", "viewed_at"]
    list_filter = ["viewed_at"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostView, PostViewAdmin)
admin.site.register(MediaLibrary, MediaLibraryAdmin)
