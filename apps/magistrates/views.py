from django.shortcuts import render

# Create your views here.

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count
from .models import Magistrate
from apps.inmates.models import Detention

class MagistrateListView(LoginRequiredMixin, ListView):
    model = Magistrate
    template_name = 'magistrates/magistrate_list.html'
    context_object_name = 'magistrates'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(court_name__icontains=search)
            )
        return queryset.annotate(detention_count=Count('detention'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

class MagistrateDetailView(LoginRequiredMixin, DetailView):
    model = Magistrate
    template_name = 'magistrates/magistrate_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detentions'] = Detention.objects.filter(
            magistrate=self.object
        ).select_related('inmate', 'prison')
        return context

class MagistrateCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Magistrate
    template_name = 'magistrates/magistrate_form.html'
    permission_required = 'magistrates.add_magistrate'
    fields = ['first_name', 'last_name', 'email', 'phone', 'court_name']
    success_url = reverse_lazy('magistrates:magistrate_list')

    def form_valid(self, form):
        messages.success(self.request, "Le magistrat a été créé avec succès.")
        return super().form_valid(form)

class MagistrateUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Magistrate
    template_name = 'magistrates/magistrate_form.html'
    permission_required = 'magistrates.change_magistrate'
    fields = ['first_name', 'last_name', 'email', 'phone', 'court_name']

    def get_success_url(self):
        return reverse_lazy('magistrates:magistrate_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Le magistrat a été mis à jour avec succès.")
        return super().form_valid(form)

class MagistrateDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Magistrate
    template_name = 'magistrates/magistrate_confirm_delete.html'
    permission_required = 'magistrates.delete_magistrate'
    success_url = reverse_lazy('magistrates:magistrate_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Le magistrat a été supprimé avec succès.")
        return super().delete(request, *args, **kwargs)


class MagistrateProfileView(LoginRequiredMixin , DetailView):
    model = Magistrate
    template_name = 'magistrates/magistrate_profile.html'
    context_object_name = 'magistrate'

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer toutes les détentions liées à ce magistrat
        detentions = Detention.objects.filter(magistrate=self.object)

        # Détentions actives (sans date de fin)
        active_detentions = detentions.filter(end_date__isnull=True)

        # Historique des détentions
        detention_history = detentions.order_by('-start_date')

        context.update({
            'detentions_count': detentions.count() ,
            'active_detentions_count': active_detentions.count() ,
            'active_detentions': active_detentions ,
            'detention_history': detention_history ,
            'detention_history_count': detention_history.count() ,
        })

        return context