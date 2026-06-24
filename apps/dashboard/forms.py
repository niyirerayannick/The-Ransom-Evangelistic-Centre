from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget

from apps.accounts.models import User
from apps.news.models import Post, Category, Tag, MediaLibrary

INPUT = "w-full rounded-lg border border-gray-200 px-3 py-2 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"


class DashboardLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20",
            "placeholder": _("Username or email"),
            "autocomplete": "username",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full rounded-xl border border-gray-200 px-4 py-3 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20",
            "placeholder": _("Password"),
            "autocomplete": "current-password",
        })
    )
    remember_me = forms.BooleanField(required=False, initial=True, label=_("Remember me"))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "profile_image", "bio", "language_preference"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "dash-input"}),
            "last_name": forms.TextInput(attrs={"class": "dash-input"}),
            "email": forms.EmailInput(attrs={"class": "dash-input"}),
            "phone": forms.TextInput(attrs={"class": "dash-input"}),
            "bio": forms.Textarea(attrs={"class": "dash-input", "rows": 3}),
            "language_preference": forms.Select(attrs={"class": "dash-input"}),
        }


class PasswordChangeDashboardForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "dash-input"}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "dash-input"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "dash-input"}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        if not self.user.check_password(cleaned.get("current_password", "")):
            self.add_error("current_password", _("Current password is incorrect."))
        p1 = cleaned.get("new_password")
        p2 = cleaned.get("confirm_password")
        if p1 and p2 and p1 != p2:
            self.add_error("confirm_password", _("Passwords do not match."))
        if p1:
            validate_password(p1, self.user)
        return cleaned


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={"class": "dash-input"}))
    password2 = forms.CharField(label=_("Confirm password"), widget=forms.PasswordInput(attrs={"class": "dash-input"}))

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "username", "email", "phone",
            "role", "profile_image", "is_active", "is_staff",
        ]
        widgets = {f: forms.TextInput(attrs={"class": "dash-input"}) for f in (
            "first_name", "last_name", "username", "email", "phone"
        )}
        widgets.update({
            "role": forms.Select(attrs={"class": "dash-input"}),
            "profile_image": forms.FileInput(attrs={"class": "dash-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "rounded"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "rounded"}),
        })

    def __init__(self, *args, actor=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)
        if actor and not actor.is_superuser:
            self.fields["role"].choices = [
                c for c in User.ROLE_CHOICES if c[0] not in ("super_admin",)
            ]
            self.fields.pop("is_staff", None)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", _("Passwords do not match."))
        if cleaned.get("password1"):
            validate_password(cleaned["password1"])
        role = cleaned.get("role")
        if self.actor and not self.actor.is_superuser and role in ("super_admin",):
            self.add_error("role", _("You cannot assign this role."))
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "username", "email", "phone",
            "role", "profile_image", "is_active", "is_staff",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "dash-input"}),
            "last_name": forms.TextInput(attrs={"class": "dash-input"}),
            "username": forms.TextInput(attrs={"class": "dash-input"}),
            "email": forms.EmailInput(attrs={"class": "dash-input"}),
            "phone": forms.TextInput(attrs={"class": "dash-input"}),
            "role": forms.Select(attrs={"class": "dash-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "rounded"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "rounded"}),
        }

    def __init__(self, *args, actor=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)
        if actor and not actor.is_superuser:
            self.fields["role"].choices = [
                c for c in User.ROLE_CHOICES if c[0] not in ("super_admin",)
            ]
            self.fields.pop("is_staff", None)


class PostReviewForm(forms.Form):
    ACTION_PUBLISH = "publish"
    ACTION_REJECT = "reject"
    ACTION_SEND_BACK = "send_back"

    action = forms.ChoiceField(
        choices=[
            (ACTION_PUBLISH, _("Publish")),
            (ACTION_REJECT, _("Reject")),
            (ACTION_SEND_BACK, _("Send back for correction")),
        ],
        widget=forms.HiddenInput,
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": _("Reason for rejection or correction notes...")}),
        label=_("Reason"),
    )


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaLibrary
        fields = ["title", "file", "alt_text", "caption", "file_type"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "dash-input"}),
            "alt_text": forms.TextInput(attrs={"class": "dash-input"}),
            "caption": forms.Textarea(attrs={"class": "dash-input", "rows": 2}),
            "file_type": forms.Select(attrs={"class": "dash-input"}),
        }

    def save(self, commit=True, user=None):
        media = super().save(commit=False)
        if user:
            media.uploaded_by = user
        if commit:
            media.save()
        return media


class PostAuthorForm(forms.ModelForm):
    LANGUAGE_FIELDS = [
        ("en", _("English")),
        ("fr", _("French")),
        ("rw", _("Kinyarwanda")),
    ]

    class Meta:
        model = Post
        fields = [
            "title_en", "title_fr", "title_rw",
            "slug_en", "slug_fr", "slug_rw",
            "excerpt_en", "excerpt_fr", "excerpt_rw",
            "content_en", "content_fr", "content_rw",
            "seo_title_en", "seo_title_fr", "seo_title_rw",
            "meta_description_en", "meta_description_fr", "meta_description_rw",
            "english_complete", "french_complete", "kinyarwanda_complete",
            "featured_image", "category", "tags", "status", "published_at",
            "is_breaking", "is_featured",
        ]
        widgets = {
            "title_en": forms.TextInput(attrs={"class": INPUT}),
            "title_fr": forms.TextInput(attrs={"class": INPUT}),
            "title_rw": forms.TextInput(attrs={"class": INPUT}),
            "slug_en": forms.TextInput(attrs={"class": INPUT}),
            "slug_fr": forms.TextInput(attrs={"class": INPUT}),
            "slug_rw": forms.TextInput(attrs={"class": INPUT}),
            "excerpt_en": forms.Textarea(attrs={"class": INPUT, "rows": 3}),
            "excerpt_fr": forms.Textarea(attrs={"class": INPUT, "rows": 3}),
            "excerpt_rw": forms.Textarea(attrs={"class": INPUT, "rows": 3}),
            "content_en": CKEditorWidget(),
            "content_fr": CKEditorWidget(),
            "content_rw": CKEditorWidget(),
            "seo_title_en": forms.TextInput(attrs={"class": INPUT}),
            "seo_title_fr": forms.TextInput(attrs={"class": INPUT}),
            "seo_title_rw": forms.TextInput(attrs={"class": INPUT}),
            "meta_description_en": forms.Textarea(attrs={"class": INPUT, "rows": 2}),
            "meta_description_fr": forms.Textarea(attrs={"class": INPUT, "rows": 2}),
            "meta_description_rw": forms.Textarea(attrs={"class": INPUT, "rows": 2}),
            "category": forms.Select(attrs={"class": INPUT}),
            "status": forms.Select(attrs={"class": INPUT}),
            "published_at": forms.DateTimeInput(attrs={"class": INPUT, "type": "datetime-local"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(is_active=True).order_by("name")
        self.fields["tags"].queryset = Tag.objects.all().order_by("name")
        if user and not user.can_publish_posts():
            self.fields["status"].choices = [
                c for c in Post.STATUS_CHOICES
                if c[0] in (Post.STATUS_DRAFT, Post.STATUS_PENDING_REVIEW, Post.STATUS_REJECTED)
            ]
            if self.instance.pk and self.instance.status == Post.STATUS_PUBLISHED:
                self.fields["status"].disabled = True
