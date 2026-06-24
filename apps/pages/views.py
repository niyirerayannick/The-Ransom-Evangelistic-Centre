from django.views.generic import DetailView
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib import messages
from django.utils.html import strip_tags
from django.utils.translation import get_language
from django.utils.translation import gettext as _

from apps.dashboard.roles import user_can_write_module
from apps.news.homepage import normalize_language_code
from .counselling_content import (
    CONTACT_INFO,
    counselling_ui_for_language,
    contact_address_for_language,
    approach_quote_for_language,
    faq_items_for_language,
    service_cards_for_language,
    trust_badges_for_language,
)
from .donation_content import FAQ_ITEMS, GOOGLE_DONATION_FORM_URL, IMPACT_ITEMS, donate_ui_for_language
from .forms import ContactMessageForm, CounsellingRequestForm, DonationPledgeForm
from .models import Book, BookCategory, Counsellor, DonationMethod, DonationProgram, LeadershipMember, Page
from .site_defaults import PAGE_SPECS


def _page_slug_for_key(key, language):
    spec = next((item for item in PAGE_SPECS if item["key"] == key), None)
    if not spec:
        return key
    return spec["slug"].get(language) or spec["slug"].get("en") or key


class PageDetailView(DetailView):
    model = Page
    template_name = "pages/page_detail.html"
    context_object_name = "page"

    template_map = {
        "who_we_are": "pages/who_we_are.html",
        "our_history": "pages/our_history.html",
        "mission_and_vision": "pages/mission_and_vision.html",
        "leadership": "pages/leadership.html",
        "what_we_do": "pages/what_we_do.html",
        "books": "pages/books.html",
        "contact": "pages/contact.html",
        "donate": "pages/donate.html",
        "find_counsellor": "pages/find_counsellor.html",
    }

    def get_object(self, queryset=None):
        slug = self.kwargs["slug"]
        slug_field = f"slug_{get_language() or 'en'}"
        queryset = Page.objects.filter(is_published=True, is_active=True).select_related("parent")
        page = queryset.filter(**{slug_field: slug}).first()
        if not page:
            page = queryset.filter(Q(slug_en=slug) | Q(slug_fr=slug) | Q(slug_rw=slug)).first()
        if not page:
            from django.http import Http404
            raise Http404
        return page

    def get_template_names(self):
        return [self.template_map.get(self.object.template_type, self.template_name)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.object
        language = normalize_language_code(get_language())

        if page.template_type == "leadership":
            members = LeadershipMember.objects.filter(is_active=True).order_by("order", "name")
            display_members = []
            team_members_data = []
            for member in members:
                display_name = member.field_for_language("name", language, fallback=True) or member.name
                display_role = member.field_for_language("role", language, fallback=True) or member.role
                display_bio = member.field_for_language("bio", language, fallback=True) or member.bio
                translation_missing = False
                translation_missing_label = ""
                if language == "fr" and (
                    member.is_translation_missing("name", "fr")
                    or member.is_translation_missing("role", "fr")
                    or member.is_translation_missing("bio", "fr")
                ):
                    translation_missing = True
                    translation_missing_label = _("French translation missing")
                elif language == "rw" and (
                    member.is_translation_missing("name", "rw")
                    or member.is_translation_missing("role", "rw")
                    or member.is_translation_missing("bio", "rw")
                ):
                    translation_missing = True
                    translation_missing_label = _("Kinyarwanda translation missing")

                display_members.append({
                    "id": member.pk,
                    "display_name": display_name,
                    "display_role": display_role,
                    "display_bio_plain": strip_tags(display_bio),
                    "photo_display_url": member.photo_display_url(),
                    "translation_missing": translation_missing,
                    "translation_missing_label": translation_missing_label,
                })
                team_members_data.append(member.to_public_dict(language))

            context["leadership_members"] = display_members
            context["team_members_data"] = team_members_data
            context["show_translation_warnings"] = (
                self.request.user.is_authenticated
                and user_can_write_module(self.request.user, "team")
            )
            context["contact_page_slug"] = _page_slug_for_key("contact", language)
            context["counsellor_page_slug"] = _page_slug_for_key("find-a-counsellor", language)

        elif page.template_type == "books":
            books = Book.objects.filter(is_active=True).select_related("category")
            query = self.request.GET.get("q", "").strip()
            category_slug = self.request.GET.get("category", "").strip()
            if query:
                books = books.filter(
                    Q(title__icontains=query)
                    | Q(author__icontains=query)
                    | Q(description__icontains=query)
                )
            if category_slug:
                books = books.filter(category__slug=category_slug)
            context["books"] = books
            context["featured_book"] = Book.objects.filter(is_active=True, is_featured=True).first()
            context["book_categories"] = BookCategory.objects.filter(is_active=True)
            context["book_query"] = query
            context["selected_category"] = category_slug

        elif page.template_type == "find_counsellor":
            context["form"] = kwargs.get("form") or CounsellingRequestForm(
                initial={"preferred_language": get_language() or "en"}
            )
            counsellors = Counsellor.objects.filter(is_active=True).order_by("order", "name")
            context["counsellors"] = [
                counsellor.to_public_dict(language) for counsellor in counsellors
            ]
            context["counselling_ui"] = counselling_ui_for_language(language)
            context["service_cards"] = service_cards_for_language(language)
            context["trust_badges"] = trust_badges_for_language(language)
            context["faq_items"] = faq_items_for_language(language)
            context["approach_quote"] = approach_quote_for_language(language)
            context["contact_phones"] = CONTACT_INFO["phones"]
            context["contact_email"] = CONTACT_INFO["email"]
            context["contact_address"] = contact_address_for_language(language)
            context["whatsapp_url"] = f"https://wa.me/{CONTACT_INFO['whatsapp_number']}"
            context["primary_phone_tel"] = "tel:+250789029994"
        elif page.template_type == "contact":
            context["form"] = kwargs.get("form") or ContactMessageForm()
        elif page.template_type == "donate":
            initial = {}
            program = self.request.GET.get("program", "").strip()
            if program in {"articles_writing", "healing_activities", "both"}:
                initial["program_to_donate"] = program
            context["form"] = kwargs.get("form") or DonationPledgeForm(initial=initial)
            context["donation_methods"] = DonationMethod.objects.filter(is_active=True).order_by("order", "name")
            context["donation_programs"] = DonationProgram.objects.filter(is_active=True).order_by("order", "title")
            context["google_donation_form_url"] = GOOGLE_DONATION_FORM_URL
            context["impact_items"] = IMPACT_ITEMS.get(language, IMPACT_ITEMS["en"])
            context["faq_items"] = FAQ_ITEMS.get(language, FAQ_ITEMS["en"])
            context["selected_program"] = program
            context["donate_ui"] = donate_ui_for_language(language)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_map = {
            "find_counsellor": (
                CounsellingRequestForm,
                None,
            ),
            "contact": (
                ContactMessageForm,
                _("Thank you. Your message has been sent to the REC team."),
            ),
            "donate": (
                DonationPledgeForm,
                None,
            ),
        }
        form_config = form_map.get(self.object.template_type)
        if not form_config:
            return redirect(self.object.get_absolute_url())
        form_class, success_message = form_config
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            if success_message is None:
                from .donation_content import donate_ui_for_language
                from .counselling_content import counselling_ui_for_language

                language = getattr(request, "LANGUAGE_CODE", None) or "en"
                if self.object.template_type == "donate":
                    success_message = donate_ui_for_language(language)["success_message"]
                elif self.object.template_type == "find_counsellor":
                    success_message = counselling_ui_for_language(language)["success_message"]
            messages.success(request, success_message)
            return redirect(self.object.get_absolute_url())
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
