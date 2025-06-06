from django.shortcuts import render , get_object_or_404
from django.views.generic import ListView , DetailView , CreateView , UpdateView , DeleteView , TemplateView , View
from django.contrib.auth.mixins import LoginRequiredMixin , PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q , Sum , Count
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from datetime import timedelta
from .models import Prison , PrisonConnection , TransferLog
from apps.inmates.models import Inmate
from .forms import PrisonForm


class PrisonDashboardView(LoginRequiredMixin , PermissionRequiredMixin , TemplateView):
    template_name = 'prisons/dashboard.html'
    permission_required = 'prisons.view_prison'

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        prisons = Prison.objects.all().order_by('province' , 'name')

        # Statistiques globales
        total_capacity = prisons.aggregate(Sum('capacity'))['capacity__sum'] or 0
        total_population = prisons.aggregate(Sum('current_population'))['current_population__sum'] or 0

        context['global_stats'] = {
            'total_prisons': prisons.count() ,
            'total_capacity': total_capacity ,
            'total_population': total_population ,
            'global_occupation_rate': (total_population / total_capacity * 100) if total_capacity > 0 else 0 ,
            'overcrowded_prisons': sum(1 for p in prisons if p.is_overcrowded())
        }

        # Données mensuelles globales
        now = timezone.now()
        monthly_data = []

        for i in range(12 , -1 , -1):
            date = now - timedelta(days=30 * i)
            month_start = date.replace(day=1 , hour=0 , minute=0 , second=0 , microsecond=0)

            total_inmates = sum(
                len([inmate for inmate in prison.inmate_set.all()
                     if inmate.admission_date <= month_start and
                     (not inmate.release_date or inmate.release_date > month_start)])
                for prison in prisons
            )

            monthly_data.append({
                'date': month_start.strftime('%Y-%m') ,
                'total': total_inmates
            })

        context.update({
            'prisons': prisons ,
            'global_monthly_data': monthly_data ,
            'prison_provinces': Prison.PROVINCES ,
        })

        return context


class PrisonListView(LoginRequiredMixin , PermissionRequiredMixin , ListView):
    model = Prison
    template_name = 'prisons/prison_list.html'
    context_object_name = 'prisons'
    permission_required = 'prisons.view_prison'
    paginate_by = 10

    def get_queryset(self):
        queryset = Prison.objects.all().order_by('province' , 'name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(province__icontains=search)
            )
        return queryset


class PrisonDetailView(LoginRequiredMixin , PermissionRequiredMixin , DetailView):
    model = Prison
    template_name = 'prisons/prison_detail.html'
    permission_required = 'prisons.view_prison'
    context_object_name = 'prison'

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        prison = self.object

        # Statistiques détaillées
        context.update({
            'statistics': prison.get_statistics() ,
            'occupation_rate': prison.get_occupation_rate() ,
            'occupation_status': prison.get_occupation_status() ,
            'monthly_data': prison.get_monthly_population_data() ,
            'upcoming_releases': prison.inmate_set.filter(
                release_date__gt=timezone.now() ,
                release_date__lte=timezone.now() + timedelta(days=30)
            ).order_by('release_date') ,
            'recent_admissions': prison.inmate_set.filter(
                admission_date__gte=timezone.now() - timedelta(days=30)
            ).order_by('-admission_date') ,
            'available_connections': prison.get_available_connections()
        })

        return context


class PrisonCreateView(LoginRequiredMixin , PermissionRequiredMixin , CreateView):
    model = Prison
    form_class = PrisonForm
    template_name = 'prisons/prison_form.html'
    permission_required = 'prisons.add_prison'
    success_url = reverse_lazy('prisons:list')

    def form_valid(self , form):
        response = super().form_valid(form)
        messages.success(self.request , f"La prison '{self.object.name}' a été créée avec succès.")
        return response


class PrisonUpdateView(LoginRequiredMixin , PermissionRequiredMixin , UpdateView):
    model = Prison
    form_class = PrisonForm
    template_name = 'prisons/prison_form.html'
    permission_required = 'prisons.change_prison'
    success_url = reverse_lazy('prisons:list')

    def form_valid(self , form):
        response = super().form_valid(form)
        messages.success(self.request , f"La prison '{self.object.name}' a été mise à jour avec succès.")
        return response


class PrisonDeleteView(LoginRequiredMixin , PermissionRequiredMixin , DeleteView):
    model = Prison
    template_name = 'prisons/prison_confirm_delete.html'
    permission_required = 'prisons.delete_prison'
    success_url = reverse_lazy('prisons:list')

    def delete(self , request , *args , **kwargs):
        prison = self.get_object()
        messages.success(request , f"La prison '{prison.name}' a été supprimée avec succès.")
        return super().delete(request , *args , **kwargs)


class TransferManagementView(LoginRequiredMixin , PermissionRequiredMixin , TemplateView):
    template_name = 'prisons/transfer_management.html'
    permission_required = 'prisons.transfer_inmates'

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        context['prisons'] = Prison.objects.all()
        return context


class PrisonInmatesView(LoginRequiredMixin , PermissionRequiredMixin , View):
    permission_required = 'prisons.view_prison'

    def get(self , request , prison_id):
        prison = get_object_or_404(Prison , id=prison_id)
        inmates = prison.inmate_set.all().values('id' , 'inmate_number' , 'first_name' , 'last_name')
        return JsonResponse(list(inmates) , safe=False)


class PrisonConnectionsView(LoginRequiredMixin , PermissionRequiredMixin , View):
    permission_required = 'prisons.view_prison'

    def get(self , request , prison_id):
        prison = get_object_or_404(Prison , id=prison_id)
        connections = prison.get_available_connections().values(
            'id' , 'prison_to__id' , 'prison_to__name' , 'max_transfer_capacity'
        )
        return JsonResponse(list(connections) , safe=False)


@method_decorator(require_POST , name='dispatch')
class ProcessTransferView(LoginRequiredMixin , PermissionRequiredMixin , View):
    permission_required = 'prisons.transfer_inmates'

    def post(self , request):
        try:
            source_prison = get_object_or_404(Prison , id=request.POST.get('source_prison'))
            destination_prison = get_object_or_404(Prison , id=request.POST.get('destination_prison'))
            inmate_ids = request.POST.getlist('inmates[]')

            connection = get_object_or_404(
                PrisonConnection ,
                prison_from=source_prison ,
                prison_to=destination_prison ,
                is_active=True
            )

            if len(inmate_ids) > connection.max_transfer_capacity:
                return JsonResponse({
                    'success': False ,
                    'message': f'Le nombre de détenus dépasse la capacité maximale de transfert ({connection.max_transfer_capacity})'
                })

            if not destination_prison.can_receive_inmates(len(inmate_ids)):
                return JsonResponse({
                    'success': False ,
                    'message': 'La prison de destination n\'a pas assez de place'
                })

            inmates = Inmate.objects.filter(id__in=inmate_ids)
            for inmate in inmates:
                inmate.prison = destination_prison
                inmate.save()

            TransferLog.objects.create(
                connection=connection ,
                number_of_inmates=len(inmate_ids) ,
                notes=f"Transfert de {len(inmate_ids)} détenu(s)"
            )

            source_prison.update_current_population()
            destination_prison.update_current_population()

            return JsonResponse({
                'success': True ,
                'message': f'{len(inmate_ids)} détenu(s) transféré(s) avec succès'
            })

        except Exception as e:
            return JsonResponse({
                'success': False ,
                'message': str(e)
            })
class PrisonGridView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'prisons/prison_grid.html'
    permission_required = 'prisons.view_prison'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prisons'] = Prison.objects.all().order_by('province', 'name')
        context['provinces'] = dict(Prison.PROVINCES)
        return context
