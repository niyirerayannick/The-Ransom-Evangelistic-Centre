from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_SUPER_ADMIN = "super_admin"
    ROLE_ADMIN = "admin"
    ROLE_EDITOR = "editor"
    ROLE_AUTHOR = "author"
    ROLE_VIEWER = "viewer"

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, _("Super Admin")),
        (ROLE_ADMIN, _("Admin")),
        (ROLE_EDITOR, _("Editor")),
        (ROLE_AUTHOR, _("Author")),
        (ROLE_VIEWER, _("Viewer")),
    ]

    LANGUAGE_PREFERENCE_CHOICES = [
        ("en", _("English")),
        ("fr", _("French")),
        ("rw", _("Kinyarwanda")),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_AUTHOR)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True)
    phone = models.CharField(max_length=50, blank=True)
    language_preference = models.CharField(
        max_length=5, choices=LANGUAGE_PREFERENCE_CHOICES, default="en", blank=True
    )
    website = models.URLField(blank=True)
    facebook_profile = models.URLField(blank=True)
    twitter_profile = models.URLField(blank=True)
    wordpress_source = models.CharField(max_length=100, blank=True)
    wordpress_user_id = models.PositiveBigIntegerField(blank=True, null=True)
    imported_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def effective_role(self):
        if self.is_superuser:
            return self.ROLE_SUPER_ADMIN
        return self.role

    @property
    def is_super_admin_role(self):
        return self.is_superuser or self.role == self.ROLE_SUPER_ADMIN

    @property
    def is_admin_role(self):
        return self.is_superuser or self.role in (self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN)

    @property
    def is_editor_role(self):
        return self.is_superuser or self.role in (
            self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_EDITOR
        )

    @property
    def is_author_role(self):
        return self.role == self.ROLE_AUTHOR

    @property
    def is_viewer_role(self):
        return self.role == self.ROLE_VIEWER

    def can_access_dashboard(self):
        if not self.is_authenticated or not self.is_active:
            return False
        return self.effective_role in (
            self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_EDITOR,
            self.ROLE_AUTHOR, self.ROLE_VIEWER,
        ) or self.is_superuser

    def can_publish_posts(self):
        return self.is_superuser or self.role in (
            self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_EDITOR
        )

    def can_review_posts(self):
        return self.can_publish_posts()

    def can_edit_post(self, post):
        if self.is_superuser or self.role in (
            self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_EDITOR
        ):
            return True
        if self.role == self.ROLE_AUTHOR and post.author_id == self.pk:
            return post.status in ("draft", "rejected", "pending_review")
        return False

    def can_delete_post(self, post):
        if self.is_superuser or self.role in (
            self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_EDITOR
        ):
            return post.status == "draft"
        if self.role == self.ROLE_AUTHOR and post.author_id == self.pk:
            return post.status == "draft"
        return False

    def get_login_redirect_url(self):
        from django.urls import reverse
        role = self.effective_role
        if role in (self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_VIEWER):
            return reverse("dashboard:home")
        return reverse("dashboard:post_list")

    def get_role_display(self):
        if self.is_superuser:
            return str(_("Super Admin"))
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
