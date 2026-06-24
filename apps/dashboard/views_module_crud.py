from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.dashboard.module_registry import get_module_config
from apps.dashboard.permissions import ModuleWriteMixin
from apps.dashboard.roles import user_can_write_module


class ModuleCreateView(ModuleWriteMixin, View):
    template_name = "dashboard/module_form.html"
    registry_key = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.config = get_module_config(self.registry_key)
        self.module_key = self.config["module_key"]

    def dispatch(self, request, *args, **kwargs):
        if not self.config.get("allow_create"):
            raise PermissionDenied
        if not user_can_write_module(request.user, self.module_key):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.config["form_class"]()
        return render(request, self.template_name, self._context(form))

    def post(self, request):
        form = self.config["form_class"](request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            messages.success(request, _("%(name)s created successfully.") % {"name": self.config["singular"]})
            return redirect(self.config["edit_url_name"], pk=obj.pk)
        return render(request, self.template_name, self._context(form))

    def _context(self, form, obj=None):
        has_i18n = any(
            f.name.endswith(("_en", "_fr", "_rw")) for f in form.visible_fields()
        )
        can_write = user_can_write_module(self.request.user, self.module_key)
        return {
            "form": form,
            "obj": obj,
            "is_create": True,
            "config": self.config,
            "has_i18n": has_i18n,
            "can_write": can_write,
            "page_title": _("Create %(item)s") % {"item": self.config["singular"]},
            "list_url": reverse(self.config["list_url_name"]),
            "submission_detail": self.config.get("submission_detail", False),
        }


class ModuleEditView(ModuleWriteMixin, View):
    template_name = "dashboard/module_form.html"
    registry_key = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.config = get_module_config(self.registry_key)
        self.module_key = self.config["module_key"]

    def get_object(self, pk):
        return get_object_or_404(self.config["model"], pk=pk)

    def get(self, request, pk):
        obj = self.get_object(pk)
        form = self.config["form_class"](instance=obj)
        return render(request, self.template_name, self._context(form, obj))

    def post(self, request, pk):
        obj = self.get_object(pk)
        form = self.config["form_class"](request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, _("%(name)s updated successfully.") % {"name": self.config["singular"]})
            return redirect(self.config["edit_url_name"], pk=obj.pk)
        return render(request, self.template_name, self._context(form, obj))

    def _context(self, form, obj):
        has_i18n = any(
            f.name.endswith(("_en", "_fr", "_rw")) for f in form.visible_fields()
        )
        can_write = user_can_write_module(self.request.user, self.module_key)
        return {
            "form": form,
            "obj": obj,
            "is_create": False,
            "config": self.config,
            "has_i18n": has_i18n,
            "can_write": can_write,
            "page_title": _("Edit %(item)s") % {"item": self.config["singular"]},
            "list_url": reverse(self.config["list_url_name"]),
            "submission_detail": self.config.get("submission_detail", False),
            "can_delete": self.config.get("allow_delete") and can_write,
            "delete_url": reverse(self.config["delete_url_name"], kwargs={"pk": obj.pk})
            if self.config.get("delete_url_name") and obj and can_write
            else None,
        }


class ModuleDeleteView(ModuleWriteMixin, View):
    registry_key = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.config = get_module_config(self.registry_key)
        self.module_key = self.config["module_key"]

    def dispatch(self, request, *args, **kwargs):
        if not self.config.get("allow_delete"):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        obj = get_object_or_404(self.config["model"], pk=pk)
        obj.delete()
        messages.success(request, _("%(name)s deleted.") % {"name": self.config["singular"]})
        return redirect(self.config["list_url_name"])
