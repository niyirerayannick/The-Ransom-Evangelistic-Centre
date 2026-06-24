from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from ckeditor.fields import RichTextField


class SiteSetting(models.Model):
    LANGUAGE_CHOICES = [("en", "English"), ("fr", "Français"), ("rw", "Kinyarwanda")]

    site_name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=500, blank=True)
    logo = models.ImageField(upload_to="site/", blank=True)
    footer_logo = models.ImageField(upload_to="site/", blank=True)
    favicon = models.ImageField(upload_to="site/", blank=True)
    footer_text = RichTextField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    phone_1 = models.CharField(max_length=50, blank=True)
    phone_2 = models.CharField(max_length=50, blank=True)
    phone_3 = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    copyright_text = models.CharField(max_length=255, blank=True)
    default_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en")
    google_analytics_id = models.CharField(max_length=50, blank=True)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_title = models.CharField(max_length=200, blank=True)
    maintenance_message = models.TextField(blank=True)
    maintenance_expected_launch_date = models.DateTimeField(blank=True, null=True)
    maintenance_contact_email = models.EmailField(blank=True)
    maintenance_show_countdown = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Site Setting")
        verbose_name_plural = _("Site Settings")

    def __str__(self):
        return self.site_name


class Menu(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=500, blank=True, help_text=_("External URL or internal path"))
    page = models.ForeignKey("pages.Page", on_delete=models.SET_NULL, blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="children")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    open_in_new_tab = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Menu")
        verbose_name_plural = _("Menus")
        ordering = ["order"]

    def __str__(self):
        return self.title

    def get_url(self):
        if self.page:
            return self.page.get_absolute_url()
        return self.url or "#"


class MenuItem(models.Model):
    LOCATION_CHOICES = [
        ("topbar", _("Top bar")),
        ("main_menu", _("Main menu")),
        ("footer_quick_links", _("Footer quick links")),
    ]

    title = models.CharField(max_length=200)
    url = models.CharField(max_length=500, blank=True)
    page = models.ForeignKey(
        "pages.Page", on_delete=models.SET_NULL, blank=True, null=True, related_name="menu_items"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="children"
    )
    location = models.CharField(max_length=30, choices=LOCATION_CHOICES, default="main_menu")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    open_in_new_tab = models.BooleanField(default=False)

    class Meta:
        ordering = ["location", "order", "title"]

    def __str__(self):
        return self.title

    def get_url(self):
        from apps.news.i18n_urls import localize_news_category_path, prefix_language_url

        language = get_language() or "en"
        if self.page_id:
            return self.page.get_absolute_url()

        url = getattr(self, f"url_{language}", None) or self.url or "#"
        url = localize_news_category_path(url, language)
        return prefix_language_url(url, language)


class HomepageSection(models.Model):
    SECTION_TYPES = [
        ("hero", _("Hero Slider")),
        ("featured", _("Featured Posts")),
        ("latest", _("Latest Posts")),
        ("category", _("Category Posts")),
        ("popular", _("Popular Posts")),
        ("newsletter", _("Newsletter Block")),
    ]
    title = models.CharField(max_length=200)
    key = models.SlugField(max_length=100, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    content = RichTextField(blank=True)
    image = models.ImageField(upload_to="homepage/", blank=True)
    button_text = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=500, blank=True)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default="latest")
    category = models.ForeignKey("news.Category", on_delete=models.SET_NULL, blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    post_count = models.IntegerField(default=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Homepage Section")
        verbose_name_plural = _("Homepage Sections")
        ordering = ["order"]

    def __str__(self):
        return f"{self.get_section_type_display()}: {self.title}"

    def field_for_language(self, field_name, language=None):
        from apps.news.homepage import normalize_language_code

        lang = normalize_language_code(language or get_language())
        for code in (lang, "en"):
            value = getattr(self, f"{field_name}_{code}", None) or ""
            if not value and code == "en":
                value = getattr(self, field_name, None) or ""
            if value:
                return value
        return ""

    def heading_for_language(self, language=None):
        return self.field_for_language("subtitle", language) or self.field_for_language("title", language)

    def button_link(self, language=None):
        from .homepage_content import resolve_homepage_button_url

        return resolve_homepage_button_url(self.button_url or "find-a-counsellor", language)


class Advertisement(models.Model):
    POSITION_CHOICES = [
        ("home_top", _("Home top")),
        ("home_after_featured", _("Home after featured")),
        ("home_middle", _("Home middle")),
        ("sidebar", _("Sidebar")),
        ("article_top", _("Article top")),
        ("article_bottom", _("Article bottom")),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="advertisements/")
    mobile_image = models.ImageField(upload_to="advertisements/", blank=True)
    link = models.URLField(blank=True)
    position = models.CharField(max_length=30, choices=POSITION_CHOICES)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    desktop_width = models.PositiveIntegerField(default=970)
    desktop_height = models.PositiveIntegerField(default=90)
    mobile_width = models.PositiveIntegerField(default=320)
    mobile_height = models.PositiveIntegerField(default=100)
    clicks = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_current(self):
        now = timezone.now()
        return (
            self.is_active
            and (not self.start_date or self.start_date <= now)
            and (not self.end_date or self.end_date >= now)
        )


class Partner(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="partners/")
    website_url = models.URLField(blank=True)
    ordering = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordering", "name"]

    def __str__(self):
        return self.name


class Slider(models.Model):
    title = models.CharField(max_length=300, verbose_name=_("Title"))
    subtitle = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to="sliders/")
    post = models.ForeignKey("news.Post", on_delete=models.SET_NULL, blank=True, null=True)
    link_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Slider")
        verbose_name_plural = _("Sliders")
        ordering = ["order"]

    def __str__(self):
        return self.title


class ImportSource(models.Model):
    STATUS_CHOICES = [
        ("imported", _("Imported")),
        ("updated", _("Updated")),
        ("skipped", _("Skipped")),
        ("error", _("Error")),
    ]

    source_database = models.CharField(max_length=100)
    source_language = models.CharField(max_length=10)
    source_type = models.CharField(max_length=50)
    old_wordpress_id = models.PositiveBigIntegerField()
    old_url = models.URLField(max_length=1000, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    imported_at = models.DateTimeField(auto_now=True)
    import_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="imported")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source_database", "source_type", "old_wordpress_id"],
                name="unique_wordpress_import_source",
            )
        ]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["source_language", "source_type"]),
        ]

    def __str__(self):
        return f"{self.source_database}:{self.source_type}:{self.old_wordpress_id}"


class Redirect(models.Model):
    LANGUAGE_CHOICES = [("en", "English"), ("fr", "French"), ("rw", "Kinyarwanda")]

    old_url = models.URLField(max_length=1000, unique=True)
    new_url = models.CharField(max_length=1000)
    source_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    content_type_name = models.CharField(max_length=50, blank=True)
    old_object_id = models.PositiveBigIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["old_url"]

    def __str__(self):
        return f"{self.old_url} → {self.new_url}"


class MediaAsset(models.Model):
    title = models.CharField(max_length=500, blank=True)
    file = models.FileField(upload_to="wordpress/", blank=True)
    remote_url = models.URLField(max_length=1000, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    alt_text = models.CharField(max_length=500, blank=True)
    caption = models.TextField(blank=True)
    description = models.TextField(blank=True)
    source_database = models.CharField(max_length=100)
    source_language = models.CharField(max_length=10)
    old_wordpress_id = models.PositiveBigIntegerField()
    old_file_path = models.CharField(max_length=1000, blank=True)
    uploaded_at = models.DateTimeField(blank=True, null=True)
    imported_at = models.DateTimeField(auto_now=True)
    is_missing = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source_database", "old_wordpress_id"],
                name="unique_wordpress_media_asset",
            )
        ]
        ordering = ["-uploaded_at", "title"]

    def __str__(self):
        return self.title or self.old_file_path or str(self.old_wordpress_id)
