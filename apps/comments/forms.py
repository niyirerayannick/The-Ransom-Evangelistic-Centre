from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["author_name", "author_email", "content"]
        widgets = {
            "author_name": forms.TextInput(attrs={"class": "form-input", "placeholder": _("Your name")}),
            "author_email": forms.EmailInput(attrs={"class": "form-input", "placeholder": _("Your email")}),
            "content": forms.Textarea(attrs={"class": "form-textarea", "rows": 5, "placeholder": _("Your comment")}),
        }
