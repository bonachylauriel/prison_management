from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin , PermissionRequiredMixin
from django.views.generic import ListView , DetailView , CreateView , TemplateView , UpdateView , DeleteView , View
from django.urls import reverse_lazy
from django.http import JsonResponse
from datetime import datetime , timedelta
from django.utils import timezone
from django.db.models import Count
from .models import Inmate , Detention , Visit
from .forms import InmateForm , DetentionForm , VisitForm , VisitApprovalForm
from apps.notifications.models import Notification
from apps.prisons.models import Prison
from django.shortcuts import redirect , get_object_or_404


class InmateListView(LoginRequiredMixin , ListView):
    model = Inmate
    template_name = 'inmates/inmate_list.html'
    context_object_name = 'inmates'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.select_related('current_prison')


class InmateDetailView(LoginRequiredMixin , DetailView):
    model = Inmate
    template_name = 'inmates/inmate_detail.html'

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        context['detentions'] = self.object.detention_set.all().select_related('prison' , 'magistrate')
        context['visits'] = self.object.visit_set.all().select_related('created_by')
        return context


class InmateCreateView(LoginRequiredMixin , PermissionRequiredMixin , CreateView):
    model = Inmate
    form_class = InmateForm
    template_name = 'inmates/inmate_form.html'
    permission_required = 'inmates.add_inmate'
    success_url = reverse_lazy('inmates:inmate_list')

    def form_valid(self , form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request , "Le détenu a été enregistré avec succès.")

        # Créer une notification
        Notification.objects.create(
            title="Nouveau détenu enregistré" ,
            message=f"Le détenu {self.object.first_name} {self.object.last_name} a été enregistré" ,
            notification_type="inmate_created"
        )
        return response


class InmateUpdateView(LoginRequiredMixin , PermissionRequiredMixin , UpdateView):
    model = Inmate
    form_class = InmateForm
    template_name = 'inmates/inmate_form.html'
    permission_required = 'inmates.change_inmate'

    def get_success_url(self):
        return reverse_lazy('inmates:inmate_detail' , kwargs={'pk': self.object.pk})

    def form_valid(self , form):
        response = super().form_valid(form)
        messages.success(self.request , "Les informations du détenu ont été mises à jour avec succès.")
        return response


class InmateDeleteView(LoginRequiredMixin , PermissionRequiredMixin , DeleteView):
    model = Inmate
    template_name = 'inmates/inmate_confirm_delete.html'
    permission_required = 'inmates.delete_inmate'
    success_url = reverse_lazy('inmates:inmate_list')

    def delete(self , request , *args , **kwargs):
        messages.success(self.request , "Le détenu a été supprimé avec succès.")
        return super().delete(request , *args , **kwargs)


class VisitCreateView(LoginRequiredMixin , PermissionRequiredMixin , CreateView):
    model = Visit
    form_class = VisitForm
    template_name = 'inmates/visit_form.html'
    permission_required = 'inmates.add_visit'

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        inmate_id = self.kwargs.get('inmate_id')
        context['inmate'] = get_object_or_404(Inmate , id=inmate_id)
        return context

    def form_valid(self , form):
        form.instance.inmate_id = self.kwargs.get('inmate_id')
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request , "La visite a été planifiée avec succès.")
        return response

    def get_success_url(self):
        return reverse_lazy('inmates:inmate_detail' , kwargs={'pk': self.kwargs['inmate_id']})


class VisitListView(LoginRequiredMixin , ListView):
    model = Visit
    template_name = 'inmates/visit_list.html'
    context_object_name = 'visits'
    paginate_by = 10

    def get_queryset(self):
        queryset = Visit.objects.all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.select_related('inmate' , 'created_by' , 'approved_by')

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Visit.STATUS_CHOICES
        return context


class VisitNetworkView(LoginRequiredMixin , PermissionRequiredMixin , TemplateView):
    template_name = 'inmates/visit_network.html'
    permission_required = 'inmates.view_visit'

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        context['prisons'] = Prison.objects.all()
        return context

    def get_timeframe_filter(self , timeframe):
        now = timezone.now()
        if timeframe == 'month':
            return now - timedelta(days=30)
        elif timeframe == 'quarter':
            return now - timedelta(days=90)
        elif timeframe == 'year':
            return now - timedelta(days=365)
        return None

    def get_network_data(self , request , prison_id=None):
        # Récupérer le paramètre timeframe
        global prison
        timeframe = request.GET.get('timeframe' , 'all')

        # Construire le filtre de base pour les visites
        visits_filter = {}
        if prison_id and prison_id != 'all':
            visits_filter['inmate__current_prison_id'] = prison_id

        # Ajouter le filtre temporel si nécessaire
        date_threshold = self.get_timeframe_filter(timeframe)
        if date_threshold:
            visits_filter['date__gte'] = date_threshold

        # Récupérer les visites filtrées
        visits = Visit.objects.filter(**visits_filter).select_related('inmate')

        # Initialiser les structures de données
        nodes = []
        edges = []
        added_inmates = set()
        added_visitors = set()
        visitor_visit_count = {}

        # Si un prison_id est spécifié, ajouter la prison comme nœud central
        if prison_id and prison_id != 'all':
            prison = Prison.objects.get(id=prison_id)
            nodes.append({
                'id': f'prison_{prison.id}' ,
                'label': prison.name ,
                'group': 'prison' ,
                'shape': 'diamond' ,
                'size': 40 ,
                'color': {
                    'background': '#6E6EFD' ,
                    'border': '#5252E0'
                }
            })

        # Traiter les visites
        for visit in visits:
            inmate = visit.inmate
            visitor_key = f"{visit.visitor_name}_{visit.visitor_id_number}"

            # Ajouter le détenu s'il n'existe pas déjà
            if inmate.id not in added_inmates:
                inmate_node = {
                    'id': f'inmate_{inmate.id}' ,
                    'label': f'{inmate.first_name} {inmate.last_name}' ,
                    'group': 'inmates' ,
                    'title': f'Détenu: {inmate.first_name} {inmate.last_name}\nN° {inmate.registration_number}'
                }
                nodes.append(inmate_node)
                added_inmates.add(inmate.id)

                # Lier le détenu à la prison si elle existe
                if prison_id and prison_id != 'all':
                    edges.append({
                        'from': f'prison_{prison.id}' ,
                        'to': f'inmate_{inmate.id}' ,
                        'color': '#2B7CE9' ,
                        'width': 2
                    })

            # Compter les visites par visiteur
            if visitor_key not in visitor_visit_count:
                visitor_visit_count[visitor_key] = 0
            visitor_visit_count[visitor_key] += 1

            # Ajouter le visiteur s'il n'existe pas déjà
            if visitor_key not in added_visitors:
                visitor_node = {
                    'id': f'visitor_{visitor_key}' ,
                    'label': visit.visitor_name ,
                    'group': 'visitors' ,
                    'title': f'Visiteur: {visit.visitor_name}\nID: {visit.visitor_id_number}' ,
                }
                nodes.append(visitor_node)
                added_visitors.add(visitor_key)

            # Ajouter la connexion visiteur-détenu
            edges.append({
                'from': f'visitor_{visitor_key}' ,
                'to': f'inmate_{inmate.id}' ,
                'label': visit.visitor_relation ,
                'title': f'Relation: {visit.visitor_relation}\nDate: {visit.date.strftime("%d/%m/%Y")}' ,
                'color': '#C5000B' ,
                'width': 1 + (visitor_visit_count[visitor_key] * 0.5)
            })

        return JsonResponse({
            'nodes': nodes ,
            'edges': edges ,
            'stats': {
                'total_visits': len(visits) ,
                'unique_inmates': len(added_inmates) ,
                'unique_visitors': len(added_visitors)
            }
        })


class VisitUpdateView(UpdateView):
    model = Visit
    template_name = 'inmates/visit_form.html'
    fields = ['inmate', 'visitor', 'date', 'duration', 'status']
    success_url = reverse_lazy('inmates:visit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la visite'
        return context
