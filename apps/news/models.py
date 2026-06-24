from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    ordering = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["ordering", "order", "name"]

    def __str__(self):
        return self.name

    def field_for_language(self, field_name, language=None):
        from django.utils.translation import get_language as active_language

        lang = (language or active_language() or "en").split("-")[0]
        if lang not in ("en", "fr", "rw"):
            lang = "en"
        value = getattr(self, f"{field_name}_{lang}", None) or ""
        if not value and lang == "en":
            value = getattr(self, field_name, None) or ""
        return value

    def get_absolute_url(self, language=None):
        from django.utils.translation import get_language as active_language
        from .i18n_urls import category_url_for_language

        lang = (language or active_language() or "en").split("-")[0]
        return category_url_for_language(self, lang)


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name

    def get_absolute_url(self, language=None):
        from django.utils.translation import get_language as active_language

        lang = (language or active_language() or "en").split("-")[0]
        slug = (
            getattr(self, f"slug_{lang}", None)
            or self.slug_en
            or self.slug_fr
            or self.slug_rw
            or self.slug
        )
        return reverse("news:tag_detail", kwargs={"slug": slug})


class Post(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PENDING_REVIEW = "pending_review"
    STATUS_PUBLISHED = "published"
    STATUS_REJECTED = "rejected"
    STATUS_ARCHIVED = "archived"

    STATUS_CHOICES = [
        (STATUS_DRAFT, _("Draft")),
        (STATUS_PENDING_REVIEW, _("Pending Review")),
        (STATUS_PUBLISHED, _("Published")),
        (STATUS_REJECTED, _("Rejected")),
        (STATUS_ARCHIVED, _("Archived")),
    ]

    LANGUAGE_CODES = ("en", "fr", "rw")
    SOURCE_LANGUAGE_CHOICES = [
        ("en", _("English")),
        ("fr", _("French")),
        ("rw", _("Kinyarwanda")),
    ]
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=550, unique=True)
    excerpt = models.TextField(blank=True)
    content = RichTextField()
    seo_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to="posts/", blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="posts")
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False)
    is_breaking = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    reading_time = models.IntegerField(editable=False, default=0)
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(blank=True, null=True, db_index=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    english_complete = models.BooleanField(default=False)
    french_complete = models.BooleanField(default=False)
    kinyarwanda_complete = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_posts",
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True)
    source_language = models.CharField(
        max_length=5,
        choices=SOURCE_LANGUAGE_CHOICES,
        blank=True,
        db_index=True,
        help_text=_("Primary imported/original language for this post."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["-published_at"]),
            models.Index(fields=["status", "is_featured"]),
            models.Index(fields=["status", "is_breaking"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self, language=None):
        from django.utils.translation import get_language as active_language
        from .i18n_urls import post_url_for_language

        lang = (language or active_language() or "en").split("-")[0]
        url = post_url_for_language(self, lang)
        if url:
            return url
        slug = self.slug_for_language(lang, fallback=True) or self.slug
        if self.published_at:
            return reverse("news:post_detail", kwargs={
                "year": self.published_at.year,
                "month": self.published_at.month,
                "day": self.published_at.day,
                "slug": slug,
            })
        return reverse("news:post_detail_slug", kwargs={"slug": slug})

    def field_for_language(self, field_name, language=None, fallback=False):
        from django.utils.translation import get_language as active_language

        lang = (language or active_language() or "en").split("-")[0]
        if lang not in self.LANGUAGE_CODES:
            lang = "en"
        value = getattr(self, f"{field_name}_{lang}", None) or ""
        if value:
            return value
        if fallback and lang != "en":
            fallback_value = getattr(self, f"{field_name}_en", None) or getattr(self, field_name, None)
            return fallback_value or ""
        if fallback and lang == "en":
            return getattr(self, field_name, None) or getattr(self, f"{field_name}_en", None) or ""
        if lang == "en" and field_name in ("title", "content", "excerpt", "slug", "seo_title", "meta_description"):
            legacy = getattr(self, field_name, None) or ""
            translated_empty = not (getattr(self, f"{field_name}_en", None) or "")
            source_ok = self.source_language in ("en", "", None)
            if legacy and translated_empty and source_ok:
                return legacy
        return ""

    def title_for_language(self, language=None, fallback=False):
        return self.field_for_language("title", language, fallback=fallback)

    def excerpt_for_language(self, language=None, fallback=False):
        return self.field_for_language("excerpt", language, fallback=fallback)

    def slug_for_language(self, language=None, fallback=False):
        return self.field_for_language("slug", language, fallback=fallback)

    def content_for_language(self, language=None, fallback=False):
        return self.field_for_language("content", language, fallback=fallback)

    def is_available_in_language(self, language=None):
        from .homepage import post_has_language_content

        return post_has_language_content(self, language)

    def available_languages(self):
        from .homepage import available_languages_for_post

        return available_languages_for_post(self)

    def save(self, *args, **kwargs):
        content_source = self.content_en or self.content or ""
        if content_source and not self.reading_time:
            import re
            plain = re.sub(r"<[^>]+>", " ", content_source)
            word_count = len(plain.split())
            self.reading_time = max(1, round(word_count / 200))
        for lang in self.LANGUAGE_CODES:
            title_field = f"title_{lang}"
            slug_field = f"slug_{lang}"
            title_value = getattr(self, title_field, None)
            slug_value = getattr(self, slug_field, None)
            if title_value and not slug_value:
                setattr(self, slug_field, slugify(title_value)[:550])
        super().save(*args, **kwargs)

    def get_localized_field(self, field_name, language=None):
        from django.utils.translation import get_language
        language = (language or get_language() or "en").split("-")[0]
        if language not in self.LANGUAGE_CODES:
            language = "en"
        value = getattr(self, f"{field_name}_{language}", None)
        if value:
            return value, False
        if language != "en":
            fallback = getattr(self, f"{field_name}_en", None) or getattr(self, field_name, None)
            return fallback, True
        return getattr(self, field_name, None) or getattr(self, f"{field_name}_en", None), False

    @property
    def localized_title(self):
        return self.title_for_language(fallback=False) or self.title_for_language(fallback=True)

    @property
    def localized_slug(self):
        return self.slug_for_language(fallback=False) or self.slug_for_language(fallback=True)

    @property
    def localized_excerpt(self):
        return self.excerpt_for_language(fallback=False) or self.excerpt_for_language(fallback=True)

    @property
    def localized_content(self):
        return self.content_for_language(fallback=False) or self.content_for_language(fallback=True)

    @property
    def localized_seo_title(self):
        return self.field_for_language("seo_title", fallback=False) or self.field_for_language("seo_title", fallback=True)

    @property
    def localized_meta_description(self):
        return self.field_for_language("meta_description", fallback=False) or self.field_for_language("meta_description", fallback=True)

    def translation_status(self):
        statuses = {}
        for lang, label, complete_field in (
            ("en", _("English"), "english_complete"),
            ("fr", _("French"), "french_complete"),
            ("rw", _("Kinyarwanda"), "kinyarwanda_complete"),
        ):
            title = getattr(self, f"title_{lang}", "") or ""
            content = getattr(self, f"content_{lang}", "") or ""
            marked_complete = getattr(self, complete_field, False)
            has_content = bool(title.strip() and content.strip())
            if marked_complete or has_content:
                statuses[lang] = {"label": label, "complete": True}
            else:
                statuses[lang] = {"label": label, "complete": False}
        return statuses

    def is_translation_missing(self, language):
        if language == "en":
            return not (self.title_en or self.title) or not (self.content_en or self.content)
        title = getattr(self, f"title_{language}", "") or ""
        content = getattr(self, f"content_{language}", "") or ""
        return not title.strip() or not content.strip()

    def increment_views(self):
        Post.objects.filter(pk=self.pk).update(views_count=models.F("views_count") + 1)

    @property
    def views(self):
        return self.views_count


class MediaLibrary(models.Model):
    FILE_IMAGE = "image"
    FILE_DOCUMENT = "document"
    FILE_VIDEO = "video"
    FILE_OTHER = "other"

    FILE_TYPE_CHOICES = [
        (FILE_IMAGE, _("Image")),
        (FILE_DOCUMENT, _("Document")),
        (FILE_VIDEO, _("Video")),
        (FILE_OTHER, _("Other")),
    ]

    title = models.CharField(max_length=300)
    file = models.FileField(upload_to="media-library/")
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default=FILE_OTHER)
    alt_text = models.CharField(max_length=300, blank=True)
    caption = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="media_uploads",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Media Library Item")
        verbose_name_plural = _("Media Library")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file and not self.file_type:
            name = self.file.name.lower()
            if name.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")):
                self.file_type = self.FILE_IMAGE
            elif name.endswith((".mp4", ".webm", ".mov")):
                self.file_type = self.FILE_VIDEO
            elif name.endswith((".pdf", ".doc", ".docx")):
                self.file_type = self.FILE_DOCUMENT
            else:
                self.file_type = self.FILE_OTHER
        super().save(*args, **kwargs)


class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="view_records")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Post View")
        verbose_name_plural = _("Post Views")
