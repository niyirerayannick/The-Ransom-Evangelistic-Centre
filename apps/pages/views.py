from django.views.generic import DetailView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import FileResponse, Http404, HttpResponse
from django.urls import reverse
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
from .pdf_render import get_pdf_page_count, render_pdf_page_jpeg
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

        if page.template_type == "who_we_are":
            from apps.news.models import Post
            from .who_we_are_content import ministry_pathways_for_language

            members = LeadershipMember.objects.filter(is_active=True).order_by("order", "name")[:4]
            leadership_members = []
            team_members_data = []
            for member in members:
                display_name = member.field_for_language("name", language, fallback=True) or member.name
                display_role = member.field_for_language("role", language, fallback=True) or member.role
                display_bio = member.field_for_language("bio", language, fallback=True) or member.bio
                leadership_members.append({
                    "id": member.pk,
                    "display_name": display_name,
                    "display_role": display_role,
                    "display_bio_plain": strip_tags(display_bio),
                    "photo_display_url": member.photo_display_url(),
                    "translation_missing": False,
                    "translation_missing_label": "",
                })
                team_members_data.append(member.to_public_dict(language))

            book_count = Book.objects.filter(is_active=True).count()
            post_count = Post.objects.filter(status=Post.STATUS_PUBLISHED).count()
            counsellor_count = Counsellor.objects.filter(is_active=True).count()

            context["leadership_members"] = leadership_members
            context["team_members_data"] = team_members_data
            context["leadership_page_slug"] = _page_slug_for_key("leadership", language)
            context["mission_page_slug"] = _page_slug_for_key("mission-and-vision", language)
            context["what_we_do_page_slug"] = _page_slug_for_key("what-we-do", language)
            context["history_page_slug"] = _page_slug_for_key("our-history", language)
            context["contact_page_slug"] = _page_slug_for_key("contact", language)
            context["counsellor_page_slug"] = _page_slug_for_key("find-a-counsellor", language)
            context["ministry_pathways"] = ministry_pathways_for_language(language)
            context["impact_stats"] = [
                {"value": "2023", "label": _("Founded with a Gospel vision")},
                {"value": f"{post_count}+", "label": _("Articles published")},
                {"value": str(book_count), "label": _("Books and resources")},
                {"value": str(counsellor_count or 1), "label": _("Counselling connections")},
            ]

        elif page.template_type == "leadership":
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
            books = list(books)
            context["books"] = books
            context["books_modal_data"] = {
                book.slug: {
                    "slug": book.slug,
                    "title": book.title,
                    "author": book.author,
                    "description": book.description or "",
                    "cover_image": book.cover_image.url if book.cover_image else "",
                    "category": book.category.name if book.category else "",
                    "language": book.get_language_display(),
                    "published_at": book.published_at.strftime("%b %d, %Y") if book.published_at else "",
                    "reader_url": reverse("pages:book_reader", kwargs={"slug": book.slug}),
                    "download_url": book.download_file.url if book.download_file else "",
                    "has_pdf": bool(book.download_file),
                }
                for book in books
            }
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


class BookReaderView(DetailView):
    model = Book
    template_name = "pages/book_reader.html"
    context_object_name = "book"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Book.objects.filter(is_active=True).select_related("category")

    def get_object(self, queryset=None):
        book = get_object_or_404(self.get_queryset(), slug=self.kwargs["slug"])
        if not book.download_file:
            from django.http import Http404
            raise Http404
        return book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = normalize_language_code(get_language())
        books_page = Page.objects.filter(
            template_type="books",
            is_active=True,
            is_published=True,
        ).first()
        if books_page:
            slug_field = f"slug_{language}"
            context["books_page_slug"] = getattr(books_page, slug_field, None) or books_page.slug_en or "books"
        else:
            context["books_page_slug"] = _page_slug_for_key("books", language)
        context["page_count"] = get_pdf_page_count(self.object.download_file)
        language = (get_language() or "en").split("-")[0]
        context["page_image_prefix"] = f"/{language}/books/{self.object.slug}/page/"
        return context


class BookPageImageView(View):
    def get(self, request, slug, page_num):
        book = get_object_or_404(Book.objects.filter(is_active=True), slug=slug)
        if not book.download_file:
            raise Http404
        try:
            image_bytes = render_pdf_page_jpeg(book.download_file, page_num)
        except ValueError as exc:
            raise Http404 from exc
        except Exception as exc:
            raise Http404 from exc
        response = HttpResponse(image_bytes, content_type="image/jpeg")
        response["Cache-Control"] = "public, max-age=86400"
        return response


class BookPdfView(DetailView):
    model = Book
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Book.objects.filter(is_active=True)

    def get(self, request, *args, **kwargs):
        book = get_object_or_404(self.get_queryset(), slug=kwargs["slug"])
        if not book.download_file:
            raise Http404
        response = FileResponse(
            book.download_file.open("rb"),
            content_type="application/pdf",
            as_attachment=False,
        )
        response["Cache-Control"] = "private, max-age=3600"
        return response
