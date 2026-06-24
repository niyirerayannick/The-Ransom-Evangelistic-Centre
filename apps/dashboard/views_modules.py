from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView

from apps.comments.models import Comment
from apps.core.models import Advertisement, HomepageSection, MenuItem, Partner, SiteSetting
from apps.dashboard.forms_modules import SiteSettingDashboardForm
from apps.dashboard.module_registry import MODULE_REGISTRY
from apps.dashboard.permissions import DashboardAccessMixin, ModuleWriteMixin
from apps.dashboard.roles import user_can_write_module
from apps.news.models import Category, Tag
from apps.newsletter.models import Subscriber
from apps.pages.models import Book, ContactMessage, CounsellingRequest, DonationPledge, Page


class ModuleListMixin(DashboardAccessMixin, ListView):
    paginate_by = 25
    search_param = "q"
    template_name = "dashboard/module_list.html"
    registry_key = None

    def get_registry(self):
        return MODULE_REGISTRY[self.registry_key]

    def get_search_query(self):
        return self.request.GET.get(self.search_param, "").strip()

    def apply_search(self, queryset):
        term = self.get_search_query()
        if term and self.search_fields:
            q = Q()
            for field in self.search_fields:
                q |= Q(**{f"{field}__icontains": term})
            queryset = queryset.filter(q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reg = self.get_registry()
        context.update({
            "page_title": self.page_title,
            "page_description": getattr(self, "page_description", ""),
            "module_key": self.module_key,
            "columns": self.columns,
            "create_url_name": reg.get("create_url_name") if reg.get("allow_create") else None,
            "edit_url_name": reg.get("edit_url_name"),
            "delete_url_name": reg.get("delete_url_name") if reg.get("allow_delete") else None,
            "add_label": getattr(self, "add_label", _("Add New")),
            "can_write": user_can_write_module(self.request.user, self.module_key),
            "empty_message": getattr(self, "empty_message", _("No records found.")),
        })
        return context


class PageListView(ModuleListMixin):
    registry_key = "pages"
    module_key = "pages"
    page_title = _("Pages")
    page_description = _("Manage institutional and ministry pages.")
    search_fields = ["title", "slug", "title_en", "title_fr"]

    columns = [
        ("title", _("Title")),
        ("slug", _("Slug")),
        ("is_published", _("Published")),
        ("updated_at", _("Updated")),
    ]

    def get_queryset(self):
        qs = Page.objects.order_by("order", "title")
        published = self.request.GET.get("published")
        if published == "yes":
            qs = qs.filter(is_published=True)
        elif published == "no":
            qs = qs.filter(is_published=False)
        return self.apply_search(qs)


class CategoryListView(ModuleListMixin):
    registry_key = "categories"
    module_key = "categories"
    page_title = _("Categories")
    page_description = _("Organize publication categories.")
    search_fields = ["name", "slug", "name_en"]
    columns = [
        ("name", _("Name")),
        ("slug", _("Slug")),
        ("is_active", _("Active")),
        ("order", _("Order")),
    ]

    def get_queryset(self):
        return self.apply_search(Category.objects.order_by("ordering", "name"))


class TagListView(ModuleListMixin):
    registry_key = "tags"
    module_key = "tags"
    page_title = _("Tags")
    page_description = _("Manage post tags.")
    search_fields = ["name", "slug", "name_en"]
    columns = [
        ("name", _("Name")),
        ("slug", _("Slug")),
        ("created_at", _("Created")),
    ]

    def get_queryset(self):
        return self.apply_search(Tag.objects.order_by("name"))


class CommentListView(ModuleListMixin):
    registry_key = "comments"
    module_key = "comments"
    page_title = _("Comments")
    page_description = _("Moderate reader comments.")
    search_fields = ["author_name", "author_email", "content"]
    columns = [
        ("author_name", _("Author")),
        ("post", _("Post")),
        ("status", _("Status")),
        ("created_at", _("Created")),
    ]

    def get_queryset(self):
        qs = Comment.objects.select_related("post").order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return self.apply_search(qs)


class BookListView(ModuleListMixin):
    registry_key = "books"
    module_key = "books"
    page_title = _("Books")
    page_description = _("Manage books and resources.")
    search_fields = ["title", "author", "slug", "title_en"]
    columns = [
        ("title", _("Title")),
        ("author", _("Author")),
        ("language", _("Language")),
        ("is_active", _("Active")),
    ]

    def get_queryset(self):
        return self.apply_search(Book.objects.order_by("-is_featured", "title"))


class CounsellingListView(ModuleListMixin):
    registry_key = "counselling"
    module_key = "counselling"
    page_title = _("Counselling Requests")
    page_description = _("Review counselling form submissions.")
    search_fields = ["full_name", "email", "phone", "message"]
    columns = [
        ("full_name", _("Name")),
        ("counselling_type", _("Type")),
        ("status", _("Status")),
        ("created_at", _("Submitted")),
    ]

    def get_queryset(self):
        qs = CounsellingRequest.objects.order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return self.apply_search(qs)


class ContactListView(ModuleListMixin):
    registry_key = "contact"
    module_key = "contact"
    page_title = _("Contact Messages")
    page_description = _("Read contact form submissions.")
    search_fields = ["full_name", "email", "subject", "message"]
    columns = [
        ("full_name", _("Name")),
        ("subject", _("Subject")),
        ("status", _("Status")),
        ("created_at", _("Received")),
    ]

    def get_queryset(self):
        qs = ContactMessage.objects.order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return self.apply_search(qs)


class DonationListView(ModuleListMixin):
    registry_key = "donations"
    module_key = "donations"
    page_title = _("Donation Pledges")
    page_description = _("Track donation pledges.")
    search_fields = ["full_name", "email", "telephone"]
    columns = [
        ("full_name", _("Name")),
        ("program_to_donate", _("Program")),
        ("amount", _("Amount")),
        ("currency", _("Currency")),
        ("payment_gateway", _("Payment")),
        ("status", _("Status")),
        ("created_at", _("Submitted")),
    ]

    def get_queryset(self):
        qs = DonationPledge.objects.order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return self.apply_search(qs)


class AdListView(ModuleListMixin):
    registry_key = "ads"
    module_key = "ads"
    page_title = _("Advertisements")
    page_description = _("Manage site advertisements.")
    search_fields = ["title", "position", "title_en"]
    columns = [
        ("title", _("Title")),
        ("position", _("Position")),
        ("is_active", _("Active")),
        ("created_at", _("Created")),
    ]

    def get_queryset(self):
        return self.apply_search(Advertisement.objects.order_by("position", "-created_at"))


class PartnerListView(ModuleListMixin):
    registry_key = "partners"
    module_key = "partners"
    page_title = _("Partners")
    page_description = _("Manage partner logos and links.")
    search_fields = ["name", "name_en"]
    columns = [
        ("name", _("Name")),
        ("website_url", _("Website")),
        ("is_active", _("Active")),
        ("ordering", _("Order")),
    ]

    def get_queryset(self):
        return self.apply_search(Partner.objects.order_by("ordering", "name"))


class MenuListView(ModuleListMixin):
    registry_key = "menus"
    module_key = "menus"
    page_title = _("Menus")
    page_description = _("Configure navigation menu items.")
    search_fields = ["title", "url", "title_en"]
    columns = [
        ("title", _("Title")),
        ("location", _("Location")),
        ("order", _("Order")),
        ("is_active", _("Active")),
    ]

    def get_queryset(self):
        qs = MenuItem.objects.order_by("location", "order", "title")
        location = self.request.GET.get("location")
        if location:
            qs = qs.filter(location=location)
        return self.apply_search(qs)


class HomepageSectionListView(ModuleListMixin):
    registry_key = "homepage"
    module_key = "homepage"
    page_title = _("Homepage Sections")
    page_description = _("Configure homepage content blocks.")
    search_fields = ["title", "section_type", "title_en"]
    columns = [
        ("title", _("Title")),
        ("section_type", _("Type")),
        ("order", _("Order")),
        ("is_active", _("Active")),
    ]

    def get_queryset(self):
        return self.apply_search(HomepageSection.objects.order_by("order", "title"))


class SubscriberListView(ModuleListMixin):
    registry_key = "subscribers"
    module_key = "subscribers"
    page_title = _("Subscribers")
    page_description = _("Newsletter subscribers.")
    search_fields = ["email", "name"]
    columns = [
        ("email", _("Email")),
        ("name", _("Name")),
        ("is_active", _("Active")),
        ("subscribed_at", _("Subscribed")),
    ]

    def get_queryset(self):
        return self.apply_search(Subscriber.objects.order_by("-subscribed_at"))


class SettingsView(ModuleWriteMixin, View):
    module_key = "settings"
    template_name = "dashboard/settings.html"

    def _get_or_create_setting(self):
        setting = SiteSetting.objects.first()
        if not setting:
            setting = SiteSetting.objects.create(site_name="The Ransom Evangelistic Centre")
        return setting

    def get(self, request):
        setting = self._get_or_create_setting()
        form = SiteSettingDashboardForm(instance=setting)
        return render(request, self.template_name, {
            "form": form,
            "site_setting": setting,
            "can_write": user_can_write_module(request.user, "settings"),
        })

    def post(self, request):
        if not user_can_write_module(request.user, "settings"):
            raise PermissionDenied
        setting = self._get_or_create_setting()
        form = SiteSettingDashboardForm(request.POST, request.FILES, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, _("Site settings updated successfully."))
            return redirect("dashboard:settings")
        return render(request, self.template_name, {
            "form": form,
            "site_setting": setting,
            "can_write": True,
        })
