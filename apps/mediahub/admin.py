from django.contrib import admin
from .models import MediaFile, Gallery, Video


class MediaFileAdmin(admin.ModelAdmin):
    list_display = ["title", "file_type", "file_size", "uploaded_by", "created_at"]
    list_filter = ["file_type", "created_at"]
    search_fields = ["title"]
    raw_id_fields = ["uploaded_by"]


class GalleryAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_published", "created_at"]
    list_filter = ["is_published"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["images"]


class VideoAdmin(admin.ModelAdmin):
    list_display = ["title", "is_published", "created_at"]
    list_filter = ["is_published"]


admin.site.register(MediaFile, MediaFileAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Video, VideoAdmin)
