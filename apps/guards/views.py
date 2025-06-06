from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView,UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages

from .models import (
    User, GuardShift, TeamUnit, Schedule, IncidentReport
)
from .forms import (
    GuardCreationForm, GuardUpdateForm, TeamUnitForm,
    ScheduleForm, IncidentReportForm, GuardShiftForm,GuardProfileForm

)

class GuardListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'guards/guard_list.html'
    context_object_name = 'guards'
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.filter(prison=self.request.user.prison)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(badge_number__icontains=query)
            )
        return queryset

class GuardCreateView(PermissionRequiredMixin, CreateView):
    model = User
    form_class = GuardCreationForm
    template_name = 'guards/guard_form.html'
    permission_required = 'guards.add_user'
    success_url = reverse_lazy('guards:guard_list')

    def form_valid(self, form):
        form.instance.prison = self.request.user.prison
        messages.success(self.request, "Le garde a été créé avec succès.")
        return super().form_valid(form)

class GuardDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'guards/guard_detail.html'
    context_object_name = 'guard'

class GuardUpdateView(PermissionRequiredMixin, UpdateView):
    model = User
    form_class = GuardUpdateForm
    template_name = 'guards/guard_form.html'
    permission_required = 'guards.change_user'
    success_url = reverse_lazy('guards:guard_list')

class ShiftListView(LoginRequiredMixin, ListView):
    model = GuardShift
    template_name = 'guards/shift_list.html'
    context_object_name = 'shifts'
    paginate_by = 10

    def get_queryset(self):
        return GuardShift.objects.filter(prison=self.request.user.prison)

class ShiftUpdateView(PermissionRequiredMixin, UpdateView):
    model = GuardShift
    form_class = GuardShiftForm
    template_name = 'guards/shift_form.html'
    permission_required = 'guards.change_guardshift'
    success_url = reverse_lazy('guards:shift_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prison'] = self.request.user.prison
        return kwargs


class TeamUnitListView(LoginRequiredMixin, ListView):
    model = TeamUnit
    template_name = 'guards/team_list.html'
    context_object_name = 'teams'
    paginate_by = 10

    def get_queryset(self):
        return TeamUnit.objects.filter(prison=self.request.user.prison)

    def form_valid(self , form):
        response = super().form_valid(form)
        messages.success(self.request , f"L'équipe '{form.instance.name}' a été créée avec succès.")
        return response

    def form_invalid(self , form):
        messages.error(self.request ,
                       "Erreur lors de la création de l'équipe. Veuillez vérifier les informations saisies.")
        return super().form_invalid(form)


class TeamUnitCreateView(PermissionRequiredMixin, CreateView):
    model = TeamUnit
    form_class = TeamUnitForm
    template_name = 'guards/team_form.html'
    permission_required = 'guards.add_teamunit'
    success_url = reverse_lazy('guards:team_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prison'] = self.request.user.prison
        return kwargs

    def form_valid(self, form):
        form.instance.prison = self.request.user.prison
        messages.success(self.request, "L'équipe a été créée avec succès.")
        return super().form_valid(form)

class TeamUnitUpdateView(PermissionRequiredMixin, UpdateView):
    model = TeamUnit
    form_class = TeamUnitForm
    template_name = 'guards/team_form.html'
    permission_required = 'guards.change_teamunit'
    success_url = reverse_lazy('guards:team_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prison'] = self.request.user.prison
        return kwargs

class ScheduleListView(LoginRequiredMixin, ListView):
    model = Schedule
    template_name = 'guards/schedule_list.html'
    context_object_name = 'schedules'
    paginate_by = 15

    def get_queryset(self):
        queryset = Schedule.objects.filter(guard__prison=self.request.user.prison)
        if not self.request.user.has_perm('guards.view_all_schedules'):
            queryset = queryset.filter(guard=self.request.user)
        return queryset

class ScheduleCreateView(PermissionRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'guards/schedule_form.html'
    permission_required = 'guards.add_schedule'
    success_url = reverse_lazy('guards:schedule_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prison'] = self.request.user.prison
        return kwargs

class IncidentReportListView(LoginRequiredMixin, ListView):
    model = IncidentReport
    template_name = 'guards/incident_list.html'
    context_object_name = 'incidents'
    paginate_by = 20

    def get_queryset(self):
        queryset = IncidentReport.objects.filter(
            reporting_guard__prison=self.request.user.prison
        )
        if not self.request.user.has_perm('guards.view_all_incidents'):
            queryset = queryset.filter(
                Q(reporting_guard=self.request.user) |
                Q(involved_guards=self.request.user)
            ).distinct()
        return queryset

class IncidentReportCreateView(LoginRequiredMixin, CreateView):
    model = IncidentReport
    form_class = IncidentReportForm
    template_name = 'guards/incident_form.html'
    success_url = reverse_lazy('guards:incident_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prison'] = self.request.user.prison
        return kwargs

    def form_valid(self, form):
        form.instance.reporting_guard = self.request.user
        messages.success(self.request, "Le rapport d'incident a été créé avec succès.")
        return super().form_valid(form)

class IncidentReportUpdateView(PermissionRequiredMixin, UpdateView):
    model = IncidentReport
    form_class = IncidentReportForm
    template_name = 'guards/incident_form.html'
    permission_required = 'guards.change_incidentreport'
    success_url = reverse_lazy('guards:incident_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prison'] = self.request.user.prison
        return kwargs

class GuardShiftCreateView(LoginRequiredMixin, CreateView):
    model = GuardShift
    form_class = GuardShiftForm
    template_name = 'guards/shift_form.html'
    success_url = reverse_lazy('guards:shift_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prison'] = self.request.user.prison
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Le service a été créé avec succès.")
        return super().form_valid(form)

    def form_valid(self , form):
        if form.instance.status == 'CLOSED' and form.instance.status != form.initial['status']:
            form.instance.closed_at = timezone.now()
            form.instance.closed_by = self.request.user
            messages.warning(
                self.request ,
                f"Le rapport d'incident '{form.instance.title}' a été fermé." ,
                extra_tags='safe'
            )
        response = super().form_valid(form)
        messages.success(
            self.request ,
            f"Le rapport d'incident a été mis à jour avec succès."
        )
        return response
class ShiftCreateView(PermissionRequiredMixin, CreateView):
    model = GuardShift
    form_class = GuardShiftForm
    template_name = 'guards/shift_form.html'
    permission_required = 'guards.add_guardshift'
    success_url = reverse_lazy('guards:shift_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prison'] = self.request.user.prison
        return kwargs

    def form_valid(self, form):
        form.instance.prison = self.request.user.prison
        messages.success(self.request, "Le service a été créé avec succès.")
        return super().form_valid(form)

class GuardProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'guards/profile.html'
    form_class = GuardProfileForm
    success_url = reverse_lazy('guards:profile')

    def get_object(self, queryset=None):
        return self.request.user
