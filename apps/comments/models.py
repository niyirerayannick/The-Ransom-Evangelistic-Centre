from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Comment(models.Model):
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]
    post = models.ForeignKey("news.Post", on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="replies")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    author_name = models.CharField(max_length=200, blank=True)
    author_email = models.EmailField(blank=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    source_database = models.CharField(max_length=100, blank=True)
    source_language = models.CharField(max_length=10, blank=True)
    old_wordpress_id = models.PositiveBigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["source_database", "old_wordpress_id"],
                condition=models.Q(old_wordpress_id__isnull=False),
                name="unique_imported_wordpress_comment",
            )
        ]

    def __str__(self):
        return f"Comment by {self.author_name or self.user} on {self.post}"

    def approve(self):
        self.status = "approved"
        self.save()

    def reject(self):
        self.status = "rejected"
        self.save()
