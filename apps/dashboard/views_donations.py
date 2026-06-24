import csv

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView

from apps.dashboard.forms_modules import (
    DonationDashboardForm,
    DonationMethodDashboardForm,
    DonationProgramDashboardForm,
)
from apps.dashboard.permissions import ModuleWriteMixin
from apps.dashboard.roles import user_can_write_module
from apps.pages.models import DonationMethod, DonationPledge, DonationProgram


class DonationPledgeListView(ModuleWriteMixin, ListView):
    module_key = "donations"
    model = DonationPledge
    template_name = "dashboard/donations/pledges.html"
    context_object_name = "pledges"
    paginate_by = 25

    def get_queryset(self):
        qs = DonationPledge.objects.order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search)
                | Q(email__icontains=search)
                | Q(telephone__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": _("Donation Pledges"),
            "can_write": user_can_write_module(self.request.user, "donations"),
            "methods_url": reverse("dashboard:donation_methods"),
            "programs_url": reverse("dashboard:donation_programs"),
        })
        return context


class DonationPledgeExportView(ModuleWriteMixin, View):
    module_key = "donations"

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="donation-pledges.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "Full Name", "Email", "Telephone", "Program", "Amount", "Currency",
            "Commitment", "Payment Gateway", "Feedback", "Status", "Created",
        ])
        for pledge in DonationPledge.objects.order_by("-created_at"):
            writer.writerow([
                pledge.full_name,
                pledge.email,
                pledge.telephone,
                pledge.get_program_to_donate_display(),
                pledge.amount,
                pledge.currency,
                pledge.get_donation_commitment_display(),
                pledge.get_payment_gateway_display(),
                pledge.feedback,
                pledge.status,
                pledge.created_at.isoformat(),
            ])
        return response


class DonationPledgeEditView(ModuleWriteMixin, View):
    module_key = "donations"
    template_name = "dashboard/donations/pledge_form.html"

    def get(self, request, pk):
        pledge = get_object_or_404(DonationPledge, pk=pk)
        form = DonationDashboardForm(instance=pledge)
        return render(request, self.template_name, {
            "form": form,
            "pledge": pledge,
            "can_write": user_can_write_module(request.user, "donations"),
            "list_url": reverse("dashboard:donation_list"),
        })

    def post(self, request, pk):
        if not user_can_write_module(request.user, "donations"):
            raise PermissionDenied
        pledge = get_object_or_404(DonationPledge, pk=pk)
        form = DonationDashboardForm(request.POST, instance=pledge)
        if form.is_valid():
            form.save()
            messages.success(request, _("Pledge updated."))
            return redirect("dashboard:donation_pledge_edit", pk=pk)
        return render(request, self.template_name, {
            "form": form,
            "pledge": pledge,
            "can_write": True,
            "list_url": reverse("dashboard:donation_list"),
        })


class DonationMethodListView(ModuleWriteMixin, ListView):
    module_key = "donations"
    model = DonationMethod
    template_name = "dashboard/donations/methods.html"
    context_object_name = "methods"
    paginate_by = 25

    def get_queryset(self):
        return DonationMethod.objects.order_by("order", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": _("Donation Methods"),
            "can_write": user_can_write_module(self.request.user, "donations"),
            "pledges_url": reverse("dashboard:donation_list"),
            "programs_url": reverse("dashboard:donation_programs"),
        })
        return context


class DonationMethodEditView(ModuleWriteMixin, View):
    module_key = "donations"
    template_name = "dashboard/donations/form.html"

    def _context(self, form, is_create=False):
        return {
            "form": form,
            "object_label": _("Donation Method"),
            "is_create": is_create,
            "can_write": user_can_write_module(self.request.user, "donations"),
            "has_i18n": True,
            "list_url": reverse("dashboard:donation_methods"),
        }

    def get(self, request, pk=None):
        if pk:
            method = get_object_or_404(DonationMethod, pk=pk)
            return render(request, self.template_name, self._context(DonationMethodDashboardForm(instance=method)))
        if not user_can_write_module(request.user, "donations"):
            raise PermissionDenied
        return render(request, self.template_name, self._context(DonationMethodDashboardForm(), is_create=True))

    def post(self, request, pk=None):
        if not user_can_write_module(request.user, "donations"):
            raise PermissionDenied
        instance = get_object_or_404(DonationMethod, pk=pk) if pk else None
        form = DonationMethodDashboardForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.name = obj.name_en or obj.name
            obj.instructions = obj.instructions_en or obj.instructions
            obj.save()
            messages.success(request, _("Donation method saved."))
            return redirect("dashboard:donation_methods")
        return render(request, self.template_name, self._context(form, is_create=not pk))


class DonationMethodDeleteView(ModuleWriteMixin, View):
    module_key = "donations"

    def post(self, request, pk):
        if not user_can_write_module(request.user, "donations"):
            raise PermissionDenied
        get_object_or_404(DonationMethod, pk=pk).delete()
        messages.success(request, _("Donation method deleted."))
        return redirect("dashboard:donation_methods")


class DonationProgramListView(ModuleWriteMixin, ListView):
    module_key = "donations"
    model = DonationProgram
    template_name = "dashboard/donations/programs.html"
    context_object_name = "programs"
    paginate_by = 25

    def get_queryset(self):
        return DonationProgram.objects.order_by("order", "title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": _("Donation Programs"),
            "can_write": user_can_write_module(self.request.user, "donations"),
            "pledges_url": reverse("dashboard:donation_list"),
            "methods_url": reverse("dashboard:donation_methods"),
        })
        return context


class DonationProgramEditView(ModuleWriteMixin, View):
    module_key = "donations"
    template_name = "dashboard/donations/form.html"

    def _context(self, form, is_create=False):
        return {
            "form": form,
            "object_label": _("Donation Program"),
            "is_create": is_create,
            "can_write": user_can_write_module(self.request.user, "donations"),
            "has_i18n": True,
            "list_url": reverse("dashboard:donation_programs"),
        }

    def get(self, request, pk=None):
        if pk:
            program = get_object_or_404(DonationProgram, pk=pk)
            return render(request, self.template_name, self._context(DonationProgramDashboardForm(instance=program)))
        if not user_can_write_module(request.user, "donations"):
            raise PermissionDenied
        return render(request, self.template_name, self._context(DonationProgramDashboardForm(), is_create=True))

    def post(self, request, pk=None):
        if not user_can_write_module(request.user, "donations"):
            raise PermissionDenied
        instance = get_object_or_404(DonationProgram, pk=pk) if pk else None
        form = DonationProgramDashboardForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.slug:
                from django.utils.text import slugify
                obj.slug = slugify(obj.title_en or obj.title)[:220]
            obj.title = obj.title_en or obj.title
            obj.description = obj.description_en or obj.description
            obj.save()
            messages.success(request, _("Donation program saved."))
            return redirect("dashboard:donation_programs")
        return render(request, self.template_name, self._context(form, is_create=not pk))


class DonationProgramDeleteView(ModuleWriteMixin, View):
    module_key = "donations"

    def post(self, request, pk):
        if not user_can_write_module(request.user, "donations"):
            raise PermissionDenied
        get_object_or_404(DonationProgram, pk=pk).delete()
        messages.success(request, _("Donation program deleted."))
        return redirect("dashboard:donation_programs")
