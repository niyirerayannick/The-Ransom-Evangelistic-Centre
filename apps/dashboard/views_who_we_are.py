from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.core.homepage_content import WHO_WE_ARE_KEY, sync_who_we_are_section
from apps.core.models import HomepageSection
from apps.dashboard.forms_modules import WhoWeAreHomeForm
from apps.dashboard.permissions import ModuleWriteMixin
from apps.dashboard.roles import user_can_write_module


class WhoWeAreEditView(ModuleWriteMixin, View):
    module_key = "homepage"
    template_name = "dashboard/who_we_are.html"

    def _get_section(self):
        return sync_who_we_are_section()

    def get(self, request):
        section = self._get_section()
        form = WhoWeAreHomeForm(instance=section)
        return render(request, self.template_name, {
            "form": form,
            "section": section,
            "can_write": user_can_write_module(request.user, "homepage"),
            "has_i18n": True,
            "page_title": _("Homepage — Who We Are"),
            "list_url": "/dashboard/homepage-sections/",
        })

    def post(self, request):
        if not user_can_write_module(request.user, "homepage"):
            raise PermissionDenied
        section = self._get_section()
        form = WhoWeAreHomeForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.key = WHO_WE_ARE_KEY
            obj.button_url = obj.button_url or "find-a-counsellor"
            obj.section_type = obj.section_type or "featured"
            obj.title = obj.title_en or obj.title
            obj.subtitle = obj.subtitle_en or obj.subtitle
            obj.content = obj.content_en or obj.content
            obj.button_text = obj.button_text_en or obj.button_text
            obj.save()
            messages.success(request, _("Who we are section updated for all languages."))
            return redirect("dashboard:who_we_are_edit")
        return render(request, self.template_name, {
            "form": form,
            "section": section,
            "can_write": True,
            "has_i18n": True,
            "page_title": _("Homepage — Who We Are"),
            "list_url": "/dashboard/homepage-sections/",
        })
