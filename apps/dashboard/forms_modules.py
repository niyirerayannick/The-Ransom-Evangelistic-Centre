"""Model forms for dashboard module editing (no Django admin redirect)."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget

from apps.comments.models import Comment
from apps.core.models import Advertisement, HomepageSection, MenuItem, Partner, SiteSetting
from apps.news.models import Category, Tag
from apps.newsletter.models import Subscriber
from apps.pages.models import Book, BookCategory, ContactMessage, CounsellingRequest, Counsellor, DonationMethod, DonationPledge, DonationProgram, LeadershipMember, Page

INPUT = "dash-input"
TEXTAREA = "dash-input"
CHECKBOX = "rounded border-gray-300 text-primary focus:ring-primary"


def _widget(field_type, **extra):
    attrs = {"class": INPUT, **extra}
    if field_type == "textarea":
        return forms.Textarea(attrs={**attrs, "rows": 3})
    if field_type == "ckeditor":
        return CKEditorWidget()
    if field_type == "checkbox":
        return forms.CheckboxInput(attrs={"class": CHECKBOX})
    if field_type == "file":
        return forms.ClearableFileInput(attrs={"class": "dash-input text-sm"})
    if field_type == "select":
        return forms.Select(attrs={"class": INPUT})
    if field_type == "number":
        return forms.NumberInput(attrs={"class": INPUT})
    if field_type == "date":
        return forms.DateInput(attrs={"class": INPUT, "type": "date"})
    if field_type == "datetime":
        return forms.DateTimeInput(attrs={"class": INPUT, "type": "datetime-local"})
    if field_type == "email":
        return forms.EmailInput(attrs={"class": INPUT})
    if field_type == "url":
        return forms.URLInput(attrs={"class": INPUT})
    return forms.TextInput(attrs={"class": INPUT})


class PageDashboardForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = [
            "title_en", "title_fr", "title_rw",
            "slug_en", "slug_fr", "slug_rw",
            "excerpt_en", "excerpt_fr", "excerpt_rw",
            "content_en", "content_fr", "content_rw",
            "meta_title_en", "meta_title_fr", "meta_title_rw",
            "meta_description_en", "meta_description_fr", "meta_description_rw",
            "template_type", "parent", "featured_image",
            "is_published", "is_active", "show_in_menu", "order",
        ]
        widgets = {
            "title_en": _widget("text"), "title_fr": _widget("text"), "title_rw": _widget("text"),
            "slug_en": _widget("text"), "slug_fr": _widget("text"), "slug_rw": _widget("text"),
            "excerpt_en": _widget("textarea"), "excerpt_fr": _widget("textarea"), "excerpt_rw": _widget("textarea"),
            "content_en": _widget("ckeditor"), "content_fr": _widget("ckeditor"), "content_rw": _widget("ckeditor"),
            "meta_title_en": _widget("text"), "meta_title_fr": _widget("text"), "meta_title_rw": _widget("text"),
            "meta_description_en": _widget("textarea"), "meta_description_fr": _widget("textarea"), "meta_description_rw": _widget("textarea"),
            "template_type": _widget("select"), "parent": _widget("select"),
            "is_published": _widget("checkbox"), "is_active": _widget("checkbox"),
            "show_in_menu": _widget("checkbox"), "order": _widget("number"),
            "featured_image": _widget("file"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].queryset = Page.objects.order_by("title")
        self.fields["parent"].required = False


class CategoryDashboardForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "name_en", "name_fr", "name_rw",
            "slug_en", "slug_fr", "slug_rw",
            "description_en", "description_fr", "description_rw",
            "image", "is_active", "order", "ordering",
        ]
        widgets = {
            "name_en": _widget("text"), "name_fr": _widget("text"), "name_rw": _widget("text"),
            "slug_en": _widget("text"), "slug_fr": _widget("text"), "slug_rw": _widget("text"),
            "description_en": _widget("textarea"), "description_fr": _widget("textarea"), "description_rw": _widget("textarea"),
            "image": _widget("file"), "is_active": _widget("checkbox"),
            "order": _widget("number"), "ordering": _widget("number"),
        }


class TagDashboardForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name_en", "name_fr", "name_rw", "slug_en", "slug_fr", "slug_rw"]
        widgets = {
            "name_en": _widget("text"), "name_fr": _widget("text"), "name_rw": _widget("text"),
            "slug_en": _widget("text"), "slug_fr": _widget("text"), "slug_rw": _widget("text"),
        }


class CommentDashboardForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["status", "content", "author_name", "author_email"]
        widgets = {
            "status": _widget("select"),
            "content": _widget("textarea"),
            "author_name": _widget("text"),
            "author_email": _widget("email"),
        }


class BookDashboardForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title_en", "title_fr", "title_rw",
            "slug", "author",
            "description_en", "description_fr", "description_rw",
            "cover_image", "category", "language", "price", "is_free",
            "download_file", "external_link", "published_at",
            "is_featured", "is_active",
        ]
        widgets = {
            "title_en": _widget("text"), "title_fr": _widget("text"), "title_rw": _widget("text"),
            "slug": _widget("text"), "author": _widget("text"),
            "description_en": _widget("ckeditor"), "description_fr": _widget("ckeditor"), "description_rw": _widget("ckeditor"),
            "cover_image": _widget("file"), "category": _widget("select"), "language": _widget("select"),
            "price": _widget("number"), "is_free": _widget("checkbox"),
            "download_file": _widget("file"), "external_link": _widget("url"),
            "published_at": _widget("date"), "is_featured": _widget("checkbox"), "is_active": _widget("checkbox"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = BookCategory.objects.filter(is_active=True)
        self.fields["slug"].required = False
        self.fields["title_en"].required = True
        self.fields["download_file"].required = True
        self.fields["download_file"].help_text = _("Upload the book as a PDF file.")
        self.fields["download_file"].widget.attrs["accept"] = "application/pdf,.pdf"
        self.fields["slug"].help_text = _("Leave blank to generate it from the English title.")

    def clean_download_file(self):
        file = self.cleaned_data.get("download_file")
        if not file:
            return file
        name = getattr(file, "name", "")
        if name and not name.lower().endswith(".pdf"):
            raise ValidationError(_("Books must be uploaded as PDF files."))
        return file

    def clean_slug(self):
        slug = (self.cleaned_data.get("slug") or "").strip()
        if slug:
            return slugify(slug)
        title = (
            self.cleaned_data.get("title_en")
            or self.cleaned_data.get("title_fr")
            or self.cleaned_data.get("title_rw")
            or ""
        )
        base = slugify(title)[:200] or "book"
        candidate = base
        counter = 1
        queryset = Book.objects.filter(slug=candidate)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        while queryset.exists():
            suffix = f"-{counter}"
            candidate = f"{base[:220 - len(suffix)]}{suffix}"
            queryset = Book.objects.filter(slug=candidate)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            counter += 1
        return candidate

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.title = obj.title_en or obj.title_fr or obj.title_rw or obj.title
        obj.description = obj.description_en or obj.description_fr or obj.description_rw or obj.description
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class CounsellingDashboardForm(forms.ModelForm):
    class Meta:
        model = CounsellingRequest
        fields = [
            "status", "full_name", "email", "phone", "preferred_language",
            "counselling_type", "preferred_contact_method", "message",
        ]
        widgets = {
            "status": _widget("select"),
            "full_name": _widget("text"),
            "email": _widget("email"),
            "phone": _widget("text"),
            "preferred_language": _widget("select"),
            "counselling_type": _widget("select"),
            "preferred_contact_method": _widget("select"),
            "message": _widget("textarea"),
        }


class CounsellingRequestDashboardForm(CounsellingDashboardForm):
    pass


class CounsellorDashboardForm(forms.ModelForm):
    class Meta:
        model = Counsellor
        fields = [
            "name_en", "name_fr", "name_rw",
            "role_en", "role_fr", "role_rw",
            "bio_en", "bio_fr", "bio_rw",
            "photo", "external_photo_url",
            "phone", "email",
            "order", "is_active",
        ]
        widgets = {
            "name_en": _widget("text"), "name_fr": _widget("text"), "name_rw": _widget("text"),
            "role_en": _widget("text"), "role_fr": _widget("text"), "role_rw": _widget("text"),
            "bio_en": _widget("ckeditor"), "bio_fr": _widget("ckeditor"), "bio_rw": _widget("ckeditor"),
            "photo": _widget("file"), "external_photo_url": _widget("url"),
            "phone": _widget("text"), "email": _widget("email"),
            "order": _widget("number"), "is_active": _widget("checkbox"),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.name = obj.name_en or obj.name
        obj.role = obj.role_en or obj.role
        obj.bio = obj.bio_en or obj.bio
        if commit:
            obj.save()
        return obj


class ContactDashboardForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["status"]
        widgets = {"status": _widget("select")}


class DonationDashboardForm(forms.ModelForm):
    class Meta:
        model = DonationPledge
        fields = [
            "status", "full_name", "email", "telephone", "program_to_donate",
            "amount", "currency", "donation_commitment", "payment_gateway", "feedback",
        ]
        widgets = {
            "status": _widget("select"),
            "full_name": _widget("text"),
            "email": _widget("email"),
            "telephone": _widget("text"),
            "program_to_donate": _widget("select"),
            "amount": _widget("number"),
            "currency": _widget("text"),
            "donation_commitment": _widget("select"),
            "payment_gateway": _widget("select"),
            "feedback": _widget("textarea"),
        }


class DonationMethodDashboardForm(forms.ModelForm):
    class Meta:
        model = DonationMethod
        fields = [
            "name_en", "name_fr", "name_rw",
            "method_type", "bank_name", "account_name", "account_number",
            "mobile_money_number", "currency", "icon",
            "instructions_en", "instructions_fr", "instructions_rw",
            "order", "is_active", "seed_key",
        ]
        widgets = {
            "name_en": _widget("text"), "name_fr": _widget("text"), "name_rw": _widget("text"),
            "method_type": _widget("select"),
            "bank_name": _widget("text"), "account_name": _widget("text"),
            "account_number": _widget("text"), "mobile_money_number": _widget("text"),
            "currency": _widget("text"), "icon": _widget("text"),
            "instructions_en": _widget("textarea"), "instructions_fr": _widget("textarea"), "instructions_rw": _widget("textarea"),
            "order": _widget("number"), "is_active": _widget("checkbox"), "seed_key": _widget("text"),
        }


class DonationProgramDashboardForm(forms.ModelForm):
    class Meta:
        model = DonationProgram
        fields = [
            "title_en", "title_fr", "title_rw",
            "slug",
            "description_en", "description_fr", "description_rw",
            "icon", "image", "order", "is_active",
        ]
        widgets = {
            "title_en": _widget("text"), "title_fr": _widget("text"), "title_rw": _widget("text"),
            "slug": _widget("text"),
            "description_en": _widget("ckeditor"), "description_fr": _widget("ckeditor"), "description_rw": _widget("ckeditor"),
            "icon": _widget("text"), "image": _widget("file"),
            "order": _widget("number"), "is_active": _widget("checkbox"),
        }


class AdvertisementDashboardForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = [
            "title_en", "title_fr", "title_rw",
            "image", "mobile_image", "link", "position",
            "is_active", "start_date", "end_date",
            "desktop_width", "desktop_height", "mobile_width", "mobile_height",
        ]
        widgets = {
            "title_en": _widget("text"), "title_fr": _widget("text"), "title_rw": _widget("text"),
            "image": _widget("file"), "mobile_image": _widget("file"), "link": _widget("url"),
            "position": _widget("select"), "is_active": _widget("checkbox"),
            "start_date": _widget("datetime"), "end_date": _widget("datetime"),
            "desktop_width": _widget("number"), "desktop_height": _widget("number"),
            "mobile_width": _widget("number"), "mobile_height": _widget("number"),
        }


class PartnerDashboardForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ["name_en", "name_fr", "name_rw", "logo", "website_url", "ordering", "is_active"]
        widgets = {
            "name_en": _widget("text"), "name_fr": _widget("text"), "name_rw": _widget("text"),
            "logo": _widget("file"), "website_url": _widget("url"),
            "ordering": _widget("number"), "is_active": _widget("checkbox"),
        }


class MenuItemDashboardForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            "title_en", "title_fr", "title_rw",
            "url_en", "url_fr", "url_rw",
            "page", "parent", "location", "order", "is_active", "open_in_new_tab",
        ]
        widgets = {
            "title_en": _widget("text"), "title_fr": _widget("text"), "title_rw": _widget("text"),
            "url_en": _widget("text"), "url_fr": _widget("text"), "url_rw": _widget("text"),
            "page": _widget("select"), "parent": _widget("select"), "location": _widget("select"),
            "order": _widget("number"), "is_active": _widget("checkbox"), "open_in_new_tab": _widget("checkbox"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["page"].queryset = Page.objects.filter(is_active=True).order_by("title")
        self.fields["parent"].queryset = MenuItem.objects.order_by("title")
        self.fields["page"].required = False
        self.fields["parent"].required = False


class WhoWeAreHomeForm(forms.ModelForm):
    class Meta:
        model = HomepageSection
        fields = [
            "subtitle_en", "subtitle_fr", "subtitle_rw",
            "title_en", "title_fr", "title_rw",
            "content_en", "content_fr", "content_rw",
            "button_text_en", "button_text_fr", "button_text_rw",
            "image", "is_active",
        ]
        widgets = {
            "subtitle_en": _widget("text"), "subtitle_fr": _widget("text"), "subtitle_rw": _widget("text"),
            "title_en": _widget("text"), "title_fr": _widget("text"), "title_rw": _widget("text"),
            "content_en": _widget("ckeditor"), "content_fr": _widget("ckeditor"), "content_rw": _widget("ckeditor"),
            "button_text_en": _widget("text"), "button_text_fr": _widget("text"), "button_text_rw": _widget("text"),
            "image": _widget("file"), "is_active": _widget("checkbox"),
        }


class HomepageSectionDashboardForm(forms.ModelForm):
    class Meta:
        model = HomepageSection
        fields = [
            "title_en", "title_fr", "title_rw",
            "subtitle_en", "subtitle_fr", "subtitle_rw",
            "content_en", "content_fr", "content_rw",
            "button_text_en", "button_text_fr", "button_text_rw",
            "key", "section_type", "category", "image", "button_url",
            "order", "is_active", "post_count",
        ]
        widgets = {
            "title_en": _widget("text"), "title_fr": _widget("text"), "title_rw": _widget("text"),
            "subtitle_en": _widget("text"), "subtitle_fr": _widget("text"), "subtitle_rw": _widget("text"),
            "content_en": _widget("ckeditor"), "content_fr": _widget("ckeditor"), "content_rw": _widget("ckeditor"),
            "button_text_en": _widget("text"), "button_text_fr": _widget("text"), "button_text_rw": _widget("text"),
            "key": _widget("text"), "section_type": _widget("select"), "category": _widget("select"),
            "image": _widget("file"), "button_url": _widget("text"),
            "order": _widget("number"), "is_active": _widget("checkbox"), "post_count": _widget("number"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(is_active=True)
        self.fields["category"].required = False


class SubscriberDashboardForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email", "name", "is_active"]
        widgets = {
            "email": _widget("email"),
            "name": _widget("text"),
            "is_active": _widget("checkbox"),
        }


class SiteSettingDashboardForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = [
            "site_name_en", "site_name_fr", "site_name_rw",
            "tagline_en", "tagline_fr", "tagline_rw",
            "logo", "footer_logo", "favicon",
            "footer_text_en", "footer_text_fr", "footer_text_rw",
            "facebook_url", "twitter_url", "x_url", "instagram_url", "youtube_url",
            "contact_email", "email", "contact_phone", "phone_1", "phone_2", "phone_3",
            "address_line_1_en", "address_line_1_fr", "address_line_1_rw",
            "address_line_2_en", "address_line_2_fr", "address_line_2_rw",
            "copyright_text_en", "copyright_text_fr", "copyright_text_rw",
            "default_language", "google_analytics_id",
            "maintenance_mode", "maintenance_title_en", "maintenance_title_fr", "maintenance_title_rw",
            "maintenance_message_en", "maintenance_message_fr", "maintenance_message_rw",
            "maintenance_expected_launch_date", "maintenance_contact_email", "maintenance_show_countdown",
        ]
        widgets = {
            "site_name_en": _widget("text"), "site_name_fr": _widget("text"), "site_name_rw": _widget("text"),
            "tagline_en": _widget("text"), "tagline_fr": _widget("text"), "tagline_rw": _widget("text"),
            "logo": _widget("file"), "footer_logo": _widget("file"), "favicon": _widget("file"),
            "footer_text_en": _widget("ckeditor"), "footer_text_fr": _widget("ckeditor"), "footer_text_rw": _widget("ckeditor"),
            "facebook_url": _widget("url"), "twitter_url": _widget("url"), "x_url": _widget("url"),
            "instagram_url": _widget("url"), "youtube_url": _widget("url"),
            "contact_email": _widget("email"), "email": _widget("email"),
            "contact_phone": _widget("text"), "phone_1": _widget("text"), "phone_2": _widget("text"), "phone_3": _widget("text"),
            "address_line_1_en": _widget("text"), "address_line_1_fr": _widget("text"), "address_line_1_rw": _widget("text"),
            "address_line_2_en": _widget("text"), "address_line_2_fr": _widget("text"), "address_line_2_rw": _widget("text"),
            "copyright_text_en": _widget("text"), "copyright_text_fr": _widget("text"), "copyright_text_rw": _widget("text"),
            "default_language": _widget("select"), "google_analytics_id": _widget("text"),
            "maintenance_mode": _widget("checkbox"),
            "maintenance_title_en": _widget("text"), "maintenance_title_fr": _widget("text"), "maintenance_title_rw": _widget("text"),
            "maintenance_message_en": _widget("textarea"), "maintenance_message_fr": _widget("textarea"), "maintenance_message_rw": _widget("textarea"),
            "maintenance_expected_launch_date": _widget("datetime"),
            "maintenance_contact_email": _widget("email"),
            "maintenance_show_countdown": _widget("checkbox"),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.maintenance_title = obj.maintenance_title_en or obj.maintenance_title
        obj.maintenance_message = obj.maintenance_message_en or obj.maintenance_message
        if commit:
            obj.save()
        return obj


class LeadershipTeamForm(forms.ModelForm):
    class Meta:
        model = LeadershipMember
        fields = [
            "name_en", "name_fr", "name_rw",
            "role_en", "role_fr", "role_rw",
            "bio_en", "bio_fr", "bio_rw",
            "photo", "external_photo_url",
            "phone", "email",
            "facebook_url", "x_url", "instagram_url", "linkedin_url",
            "order", "is_active",
        ]
        widgets = {
            "name_en": _widget("text"), "name_fr": _widget("text"), "name_rw": _widget("text"),
            "role_en": _widget("text"), "role_fr": _widget("text"), "role_rw": _widget("text"),
            "bio_en": _widget("ckeditor"), "bio_fr": _widget("ckeditor"), "bio_rw": _widget("ckeditor"),
            "photo": _widget("file"), "external_photo_url": _widget("url"),
            "phone": _widget("text"), "email": _widget("email"),
            "facebook_url": _widget("url"), "x_url": _widget("url"),
            "instagram_url": _widget("url"), "linkedin_url": _widget("url"),
            "order": _widget("number"), "is_active": _widget("checkbox"),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.name = obj.name_en or obj.name
        obj.role = obj.role_en or obj.role
        obj.bio = obj.bio_en or obj.bio
        if commit:
            obj.save()
        return obj
