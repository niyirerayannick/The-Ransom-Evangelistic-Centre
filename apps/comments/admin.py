from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ["author_name", "post", "content_short", "status", "source_language", "old_wordpress_id", "created_at"]
    list_filter = ["status", "source_language", "source_database", "created_at"]
    search_fields = ["author_name", "author_email", "content"]
    readonly_fields = ["source_database", "source_language", "old_wordpress_id", "created_at"]
    actions = ["approve_comments", "reject_comments"]

    def content_short(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_short.short_description = _("Comment")

    def approve_comments(self, request, queryset):
        queryset.update(status="approved")
    approve_comments.short_description = _("Approve selected comments")

    def reject_comments(self, request, queryset):
        queryset.update(status="rejected")
    reject_comments.short_description = _("Reject selected comments")


admin.site.register(Comment, CommentAdmin)
