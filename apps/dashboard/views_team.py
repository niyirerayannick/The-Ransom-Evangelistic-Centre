from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView

from apps.dashboard.forms_modules import LeadershipTeamForm
from apps.dashboard.permissions import ModuleWriteMixin
from apps.dashboard.roles import user_can_write_module
from apps.pages.models import LeadershipMember


class TeamListView(ModuleWriteMixin, ListView):
    module_key = "team"
    model = LeadershipMember
    template_name = "dashboard/team/list.html"
    context_object_name = "members"
    paginate_by = 25

    def get_queryset(self):
        qs = LeadershipMember.objects.order_by("order", "name")
        search = self.request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(name_en__icontains=search)
                | Q(name_fr__icontains=search)
                | Q(name_rw__icontains=search)
                | Q(role__icontains=search)
                | Q(role_en__icontains=search)
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
            "page_title": _("Team / Leadership"),
            "can_write": user_can_write_module(self.request.user, "team"),
        })
        return context


class TeamCreateView(ModuleWriteMixin, View):
    module_key = "team"
    template_name = "dashboard/team/form.html"

    def dispatch(self, request, *args, **kwargs):
        if not user_can_write_module(request.user, "team"):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, self._context(LeadershipTeamForm(), is_create=True))

    def post(self, request):
        form = LeadershipTeamForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            messages.success(request, _("Team member created."))
            return redirect("dashboard:team_edit", pk=member.pk)
        return render(request, self.template_name, self._context(form, is_create=True))

    def _context(self, form, is_create=False, member=None):
        return {
            "form": form,
            "member": member,
            "is_create": is_create,
            "can_write": True,
            "has_i18n": True,
            "page_title": _("Add team member") if is_create else _("Edit team member"),
            "list_url": reverse("dashboard:team_list"),
        }


class TeamEditView(ModuleWriteMixin, View):
    module_key = "team"
    template_name = "dashboard/team/form.html"

    def get(self, request, pk):
        member = get_object_or_404(LeadershipMember, pk=pk)
        form = LeadershipTeamForm(instance=member)
        return render(request, self.template_name, TeamCreateView()._context(form, member=member))

    def post(self, request, pk):
        if not user_can_write_module(request.user, "team"):
            raise PermissionDenied
        member = get_object_or_404(LeadershipMember, pk=pk)
        form = LeadershipTeamForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, _("Team member updated."))
            return redirect("dashboard:team_edit", pk=member.pk)
        ctx = TeamCreateView()._context(form, member=member)
        ctx["can_write"] = True
        return render(request, self.template_name, ctx)


class TeamToggleActiveView(ModuleWriteMixin, View):
    module_key = "team"

    def post(self, request, pk):
        if not user_can_write_module(request.user, "team"):
            raise PermissionDenied
        member = get_object_or_404(LeadershipMember, pk=pk)
        member.is_active = not member.is_active
        member.save(update_fields=["is_active"])
        state = _("activated") if member.is_active else _("deactivated")
        messages.success(request, _("%(name)s %(state)s.") % {"name": member.name, "state": state})
        return redirect("dashboard:team_list")


class TeamDeleteView(ModuleWriteMixin, View):
    module_key = "team"

    def post(self, request, pk):
        if not user_can_write_module(request.user, "team"):
            raise PermissionDenied
        member = get_object_or_404(LeadershipMember, pk=pk)
        member.delete()
        messages.success(request, _("Team member deleted."))
        return redirect("dashboard:team_list")
