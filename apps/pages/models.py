from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from ckeditor.fields import RichTextField


class Page(models.Model):
    TEMPLATE_CHOICES = [
        ("default", _("Default page")),
        ("who_we_are", _("Who we are")),
        ("our_history", _("Our history")),
        ("mission_and_vision", _("Mission and vision")),
        ("leadership", _("Leadership")),
        ("what_we_do", _("What we do")),
        ("books", _("Books")),
        ("contact", _("Contact")),
        ("donate", _("Donate")),
        ("find_counsellor", _("Find a counsellor")),
        ("policy", _("Policy")),
    ]

    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=550, unique=True)
    content = RichTextField()
    excerpt = models.TextField(blank=True)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_CHOICES, default="default")
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True, related_name="children"
    )
    seo_title = models.CharField(max_length=200, blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to="pages/", blank=True)
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    show_in_menu = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        slug = self.slug or self.slug_en or self.slug_fr or self.slug_rw
        return reverse("pages:page_detail", kwargs={"slug": slug})


class LeadershipMember(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    role = models.CharField(max_length=200)
    photo = models.ImageField(upload_to="team/", blank=True)
    external_photo_url = models.URLField(blank=True)
    bio = RichTextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    facebook_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Leadership team member")
        verbose_name_plural = _("Leadership team members")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name_en or self.name)[:200] or "member"
            slug = base
            counter = 1
            while LeadershipMember.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def field_for_language(self, field_name, language=None, fallback=False):
        from django.utils.translation import get_language as active_language

        lang = (language or active_language() or "en").split("-")[0]
        if lang not in ("en", "fr", "rw"):
            lang = "en"
        value = getattr(self, f"{field_name}_{lang}", None) or ""
        if value:
            return value
        if fallback and lang != "en":
            return getattr(self, f"{field_name}_en", None) or getattr(self, field_name, None) or ""
        if fallback and lang == "en":
            return getattr(self, field_name, None) or getattr(self, f"{field_name}_en", None) or ""
        if lang == "en" and field_name in ("name", "role", "bio"):
            legacy = getattr(self, field_name, None) or ""
            translated_empty = not (getattr(self, f"{field_name}_en", None) or "")
            if legacy and translated_empty:
                return legacy
        return ""

    def is_translation_missing(self, field_name, language=None):
        from django.utils.translation import get_language as active_language

        lang = (language or active_language() or "en").split("-")[0]
        if lang == "en":
            return False
        value = (getattr(self, f"{field_name}_{lang}", None) or "").strip()
        if field_name == "bio":
            from django.utils.html import strip_tags
            return not strip_tags(value).strip()
        return not value

    def photo_display_url(self):
        if self.photo:
            return self.photo.url
        return self.external_photo_url or ""

    def to_public_dict(self, language=None):
        from django.utils.html import strip_tags

        lang = language or "en"
        name = self.field_for_language("name", lang, fallback=True) or self.name
        role = self.field_for_language("role", lang, fallback=True) or self.role
        bio = self.field_for_language("bio", lang, fallback=True) or self.bio
        return {
            "id": self.pk,
            "slug": self.slug,
            "name": name,
            "role": role,
            "bio": bio,
            "bio_plain": strip_tags(bio),
            "photo_url": self.photo_display_url(),
            "phone": self.phone,
            "email": self.email,
            "facebook_url": self.facebook_url,
            "x_url": self.x_url,
            "instagram_url": self.instagram_url,
            "linkedin_url": self.linkedin_url,
            "missing_fr": self.is_translation_missing("name", "fr")
                or self.is_translation_missing("role", "fr")
                or self.is_translation_missing("bio", "fr"),
            "missing_rw": self.is_translation_missing("name", "rw")
                or self.is_translation_missing("role", "rw")
                or self.is_translation_missing("bio", "rw"),
        }


class BookCategory(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Book categories"

    def __str__(self):
        return self.name


class Book(models.Model):
    LANGUAGE_CHOICES = [
        ("en", _("English")),
        ("fr", _("French")),
        ("rw", _("Kinyarwanda")),
        ("multi", _("Multilingual")),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True)
    cover_image = models.ImageField(upload_to="books/", blank=True)
    author = models.CharField(max_length=200)
    description = RichTextField(blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="en")
    category = models.ForeignKey(
        BookCategory, on_delete=models.SET_NULL, blank=True, null=True, related_name="books"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_free = models.BooleanField(default=False)
    download_file = models.FileField(upload_to="books/files/", blank=True)
    external_link = models.URLField(blank=True)
    published_at = models.DateField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_featured", "-published_at", "title"]

    def __str__(self):
        return self.title


class CounsellingRequest(models.Model):
    TYPE_CHOICES = [
        ("trauma", _("Trauma support")),
        ("spiritual", _("Spiritual counselling")),
        ("family", _("Family counselling")),
        ("healing", _("Healing support")),
        ("general", _("General support")),
    ]
    CONTACT_CHOICES = [
        ("phone", _("Phone")),
        ("email", _("Email")),
        ("whatsapp", _("WhatsApp")),
    ]
    STATUS_CHOICES = [
        ("new", _("New")),
        ("contacted", _("Contacted")),
        ("in_progress", _("In progress")),
        ("closed", _("Closed")),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    preferred_language = models.CharField(max_length=10, choices=Book.LANGUAGE_CHOICES[:3], default="en")
    counselling_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField()
    preferred_contact_method = models.CharField(max_length=20, choices=CONTACT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.get_counselling_type_display()}"


class Counsellor(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    role = models.CharField(max_length=250)
    photo = models.ImageField(upload_to="counsellors/", blank=True)
    external_photo_url = models.URLField(blank=True)
    bio = RichTextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    seed_key = models.SlugField(max_length=80, blank=True, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Counsellor")
        verbose_name_plural = _("Counsellors")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name_en or self.name)[:200] or "counsellor"
            slug = base
            counter = 1
            while Counsellor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def field_for_language(self, field_name, language=None, fallback=True):
        from django.utils.translation import get_language as active_language

        lang = (language or active_language() or "en").split("-")[0]
        if lang not in ("en", "fr", "rw"):
            lang = "en"
        value = getattr(self, f"{field_name}_{lang}", None) or ""
        if value:
            return value
        if fallback:
            return getattr(self, f"{field_name}_en", None) or getattr(self, field_name, None) or ""
        return getattr(self, field_name, None) or ""

    def photo_display_url(self):
        if self.photo:
            return self.photo.url
        return self.external_photo_url or ""

    def to_public_dict(self, language=None):
        from django.utils.html import strip_tags

        lang = language or "en"
        bio = self.field_for_language("bio", lang, fallback=True)
        return {
            "id": self.pk,
            "slug": self.slug,
            "name": self.field_for_language("name", lang, fallback=True) or self.name,
            "role": self.field_for_language("role", lang, fallback=True) or self.role,
            "bio_html": bio,
            "bio_plain": strip_tags(bio),
            "photo_url": self.photo_display_url(),
            "phone": self.phone,
            "email": self.email,
        }


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ("new", _("New")),
        ("read", _("Read")),
        ("replied", _("Replied")),
        ("closed", _("Closed")),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=250)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name}: {self.subject}"


class DonationMethod(models.Model):
    TYPE_CHOICES = [
        ("bank", _("Bank transfer")),
        ("mobile_money", _("Mobile money")),
        ("online", _("Online payment")),
        ("other", _("Other")),
    ]

    name = models.CharField(max_length=200)
    method_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    account_name = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    mobile_money_number = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=10, blank=True, default="RWF")
    instructions = models.TextField(blank=True)
    icon = models.CharField(max_length=20, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    seed_key = models.SlugField(max_length=80, blank=True, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def field_for_language(self, field_name, language=None, fallback=True):
        from django.utils.translation import get_language as active_language

        lang = (language or active_language() or "en").split("-")[0]
        if lang not in ("en", "fr", "rw"):
            lang = "en"
        value = getattr(self, f"{field_name}_{lang}", None) or ""
        if value:
            return value
        if fallback:
            return getattr(self, f"{field_name}_en", None) or getattr(self, field_name, None) or ""
        return getattr(self, field_name, None) or ""

    def copy_value(self):
        if self.method_type == "mobile_money":
            return self.mobile_money_number
        return self.account_number


class DonationProgram(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to="donations/programs/", blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def field_for_language(self, field_name, language=None, fallback=True):
        from django.utils.translation import get_language as active_language

        lang = (language or active_language() or "en").split("-")[0]
        if lang not in ("en", "fr", "rw"):
            lang = "en"
        value = getattr(self, f"{field_name}_{lang}", None) or ""
        if value:
            return value
        if fallback:
            return getattr(self, f"{field_name}_en", None) or getattr(self, field_name, None) or ""
        return getattr(self, field_name, None) or ""

    @property
    def program_key(self):
        return self.slug.replace("-", "_")


class DonationPledge(models.Model):
    PROGRAM_CHOICES = [
        ("articles_writing", _("Articles Writing")),
        ("healing_activities", _("Healing activities")),
        ("both", _("Both")),
    ]
    COMMITMENT_CHOICES = [
        ("one_time", _("One time")),
        ("monthly", _("Monthly")),
        ("quarterly", _("Quarterly")),
        ("annually", _("Annually")),
    ]
    GATEWAY_CHOICES = [
        ("cash", _("Cash")),
        ("mobile_money", _("Mobile Money")),
        ("bank_transfer", _("Bank Transfer")),
    ]
    STATUS_CHOICES = [
        ("new", _("New")),
        ("contacted", _("Contacted")),
        ("confirmed", _("Confirmed")),
        ("completed", _("Completed")),
        ("cancelled", _("Cancelled")),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=50)
    program_to_donate = models.CharField(max_length=30, choices=PROGRAM_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="RWF")
    donation_commitment = models.CharField(max_length=20, choices=COMMITMENT_CHOICES, default="one_time")
    payment_gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.amount} {self.currency}"
