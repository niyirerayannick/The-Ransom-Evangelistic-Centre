from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView

from apps.dashboard.forms_modules import CounsellingRequestDashboardForm, CounsellorDashboardForm
from apps.dashboard.permissions import ModuleWriteMixin
from apps.dashboard.roles import user_can_write_module
from apps.pages.models import CounsellingRequest, Counsellor


class CounsellorListView(ModuleWriteMixin, ListView):
    module_key = "counsellors"
    model = Counsellor
    template_name = "dashboard/counsellors/list.html"
    context_object_name = "counsellors"
    paginate_by = 25

    def get_queryset(self):
        qs = Counsellor.objects.order_by("order", "name")
        search = self.request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(name_en__icontains=search)
                | Q(name_fr__icontains=search)
                | Q(name_rw__icontains=search)
                | Q(role__icontains=search)
            )
        status = self.request.GET.get("status")
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": _("Counsellors"),
            "can_write": user_can_write_module(self.request.user, "counsellors"),
            "requests_url": reverse("dashboard:counselling_requests"),
        })
        return context


class CounsellorEditView(ModuleWriteMixin, View):
    module_key = "counsellors"
    template_name = "dashboard/counsellors/form.html"

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get("pk") is None and not user_can_write_module(request.user, "counsellors"):
            raise PermissionDenied
        if kwargs.get("pk") is not None and request.method == "POST" and not user_can_write_module(request.user, "counsellors"):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk=None):
        counsellor = get_object_or_404(Counsellor, pk=pk) if pk else None
        form = CounsellorDashboardForm(instance=counsellor)
        return render(request, self.template_name, self._context(form, counsellor=counsellor, is_create=pk is None))

    def post(self, request, pk=None):
        counsellor = get_object_or_404(Counsellor, pk=pk) if pk else None
        form = CounsellorDashboardForm(request.POST, request.FILES, instance=counsellor)
        if form.is_valid():
            counsellor = form.save()
            messages.success(request, _("Counsellor saved."))
            return redirect("dashboard:counsellor_edit", pk=counsellor.pk)
        return render(request, self.template_name, self._context(form, counsellor=counsellor, is_create=pk is None))

    def _context(self, form, counsellor=None, is_create=False):
        return {
            "form": form,
            "counsellor": counsellor,
            "is_create": is_create,
            "can_write": user_can_write_module(self.request.user, "counsellors"),
            "has_i18n": True,
            "page_title": _("Add counsellor") if is_create else _("Edit counsellor"),
            "list_url": reverse("dashboard:counsellor_list"),
        }


class CounsellorToggleActiveView(ModuleWriteMixin, View):
    module_key = "counsellors"

    def post(self, request, pk):
        if not user_can_write_module(request.user, "counsellors"):
            raise PermissionDenied
        counsellor = get_object_or_404(Counsellor, pk=pk)
        counsellor.is_active = not counsellor.is_active
        counsellor.save(update_fields=["is_active"])
        state = _("activated") if counsellor.is_active else _("deactivated")
        messages.success(request, _("%(name)s %(state)s.") % {"name": counsellor.name, "state": state})
        return redirect("dashboard:counsellor_list")


class CounsellorDeleteView(ModuleWriteMixin, View):
    module_key = "counsellors"

    def post(self, request, pk):
        if not user_can_write_module(request.user, "counsellors"):
            raise PermissionDenied
        counsellor = get_object_or_404(Counsellor, pk=pk)
        counsellor.delete()
        messages.success(request, _("Counsellor deleted."))
        return redirect("dashboard:counsellor_list")


class CounsellingRequestListView(ModuleWriteMixin, ListView):
    module_key = "counselling"
    model = CounsellingRequest
    template_name = "dashboard/counselling_requests/list.html"
    context_object_name = "requests"
    paginate_by = 25

    def get_queryset(self):
        qs = CounsellingRequest.objects.order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
                | Q(message__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": _("Counselling Requests"),
            "can_write": user_can_write_module(self.request.user, "counselling"),
            "counsellors_url": reverse("dashboard:counsellor_list"),
        })
        return context


class CounsellingRequestEditView(ModuleWriteMixin, View):
    module_key = "counselling"
    template_name = "dashboard/counselling_requests/form.html"

    def get(self, request, pk):
        counselling_request = get_object_or_404(CounsellingRequest, pk=pk)
        form = CounsellingRequestDashboardForm(instance=counselling_request)
        return render(request, self.template_name, {
            "form": form,
            "counselling_request": counselling_request,
            "can_write": user_can_write_module(request.user, "counselling"),
            "list_url": reverse("dashboard:counselling_requests"),
            "page_title": _("Counselling Request"),
        })

    def post(self, request, pk):
        if not user_can_write_module(request.user, "counselling"):
            raise PermissionDenied
        counselling_request = get_object_or_404(CounsellingRequest, pk=pk)
        form = CounsellingRequestDashboardForm(request.POST, instance=counselling_request)
        if form.is_valid():
            form.save()
            messages.success(request, _("Counselling request updated."))
            return redirect("dashboard:counselling_request_edit", pk=pk)
        return render(request, self.template_name, {
            "form": form,
            "counselling_request": counselling_request,
            "can_write": True,
            "list_url": reverse("dashboard:counselling_requests"),
            "page_title": _("Counselling Request"),
        })
