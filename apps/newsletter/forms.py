from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Subscriber


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email", "name"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": _("Your email address")}),
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": _("Your name (optional)")}),
        }
