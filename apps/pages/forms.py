from django import forms
from django.utils.translation import get_language

from .counselling_content import (
    form_choices_for_language as counselling_form_choices_for_language,
    form_labels_for_language as counselling_form_labels_for_language,
)
from .donation_content import form_choices_for_language, form_labels_for_language
from .models import ContactMessage, CounsellingRequest, DonationPledge


INPUT_CLASS = (
    "mt-2 w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm "
    "outline-none transition focus:border-[#d39200] focus:ring-2 focus:ring-[#d39200]/20"
)


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                continue
            widget.attrs["class"] = INPUT_CLASS


class CounsellingRequestForm(StyledModelForm):
    class Meta:
        model = CounsellingRequest
        fields = [
            "full_name", "email", "phone", "preferred_language",
            "counselling_type", "preferred_contact_method", "message",
        ]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
            "preferred_language": forms.Select(),
            "counselling_type": forms.Select(),
            "preferred_contact_method": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        language = (get_language() or "en").split("-")[0]
        labels = counselling_form_labels_for_language(language)
        choices = counselling_form_choices_for_language(language)
        for field_name, label in labels.items():
            if field_name in self.fields:
                self.fields[field_name].label = label
        for field_name, field_choices in choices.items():
            if field_name in self.fields:
                self.fields[field_name].choices = field_choices


class ContactMessageForm(StyledModelForm):
    class Meta:
        model = ContactMessage
        fields = ["full_name", "email", "phone", "subject", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 6})}


class DonationPledgeForm(StyledModelForm):
    class Meta:
        model = DonationPledge
        fields = [
            "full_name",
            "email",
            "telephone",
            "program_to_donate",
            "amount",
            "currency",
            "donation_commitment",
            "payment_gateway",
            "feedback",
        ]
        widgets = {
            "feedback": forms.Textarea(attrs={"rows": 4}),
            "program_to_donate": forms.Select(),
            "donation_commitment": forms.Select(),
            "payment_gateway": forms.Select(),
            "currency": forms.Select(choices=[("RWF", "RWF"), ("USD", "USD")]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        language = (get_language() or "en").split("-")[0]
        labels = form_labels_for_language(language)
        choices = form_choices_for_language(language)
        for field_name, label in labels.items():
            if field_name in self.fields:
                self.fields[field_name].label = label
        for field_name, field_choices in choices.items():
            if field_name in self.fields:
                self.fields[field_name].choices = field_choices
        self.fields["full_name"].required = True
        self.fields["telephone"].required = True
        self.fields["program_to_donate"].required = True
        self.fields["amount"].required = True
        self.fields["payment_gateway"].required = True
        self.fields["email"].required = False
