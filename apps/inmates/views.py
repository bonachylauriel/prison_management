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
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import csv
import xlsxwriter
from io import BytesIO
from django.http import HttpResponse
from django.http import Http404
from django.utils.timezone import localtime



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
    #SELECTION PAR TEMPS
    def get(self , request , *args , **kwargs):
        if 'data' in request.path:
            prison_id = kwargs.get('prison_id' , 'all')
            return self.get_network_data(request , prison_id)
        return super().get(request , *args , **kwargs)

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


class VisitDeleteView(LoginRequiredMixin , DeleteView):
    model = Visit
    template_name = 'inmates/visit_confirm_delete.html'
    success_url = reverse_lazy('inmates:visit_list')

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Supprimer la visite'
        return context


class VisitApprovalView(LoginRequiredMixin , UpdateView):
    model = Visit
    template_name = 'inmates/visit_approval.html'
    fields = ['status' , 'rejection_reason']
    success_url = reverse_lazy('inmates:visit_list')

    def form_valid(self , form):
        response = super().form_valid(form)
        if self.object.status == 'approved':
            messages.success(self.request , 'La visite a été approuvée avec succès.')
        elif self.object.status == 'rejected':
            messages.warning(self.request , 'La visite a été refusée.')
        return response

    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Approbation de la visite"
        return context


class InmateStatisticsView(LoginRequiredMixin , View):
    def get(self , request , *args , **kwargs):
        context = self.get_statistics()
        return render(request , 'inmates/statistics.html' , context)

    def get_statistics(self):
        return {
            'total_inmates': Inmate.objects.count() ,
            'active_inmates': Inmate.objects.filter(detention__end_date__isnull=True).distinct().count() ,
            'by_nationality': Inmate.objects.values('nationality').annotate(count=Count('id')) ,
            'by_gender': Inmate.objects.values('gender').annotate(count=Count('id')) ,
        }


class CriminalRecordPDFView(LoginRequiredMixin , View):
    def get(self , request , pk):
        inmate = get_object_or_404(Inmate , pk=pk)

        # Créer un buffer pour le PDF
        buffer = BytesIO()

        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer ,
            pagesize=A4 ,
            rightMargin=72 ,
            leftMargin=72 ,
            topMargin=72 ,
            bottomMargin=72
        )

        # Contenu du document
        elements = []
        styles = getSampleStyleSheet()

        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle' ,
            parent=styles['Heading1'] ,
            fontSize=16 ,
            spaceAfter=30 ,
            alignment=1  # Center alignment
        )

        # Titre
        elements.append(Paragraph(f"Casier Judiciaire" , title_style))
        elements.append(Paragraph(f"Numéro d'écrou : {inmate.registration_number}" , styles['Heading2']))
        elements.append(Spacer(1 , 12))

        # Informations du détenu
        inmate_info = [
            ['Nom' , inmate.last_name] ,
            ['Prénom' , inmate.first_name] ,
            ['Date de naissance' , inmate.birth_date.strftime('%d/%m/%Y')] ,
            ['Nationalité' , inmate.nationality] ,
        ]

        table = Table(inmate_info , colWidths=[100 , 300])
        table.setStyle(TableStyle([
            ('FONTNAME' , (0 , 0) , (-1 , -1) , 'Helvetica') ,
            ('FONTSIZE' , (0 , 0) , (-1 , -1) , 10) ,
            ('GRID' , (0 , 0) , (-1 , -1) , 1 , colors.black) ,
            ('BACKGROUND' , (0 , 0) , (0 , -1) , colors.lightgrey) ,
            ('PADDING' , (0 , 0) , (-1 , -1) , 6) ,
        ]))
        elements.append(table)
        elements.append(Spacer(1 , 20))

        # Historique des détentions
        elements.append(Paragraph("Historique des détentions" , styles['Heading2']))
        elements.append(Spacer(1 , 12))

        detentions = inmate.get_criminal_record()
        if detentions:
            detention_data = [['Prison' , 'Date d\'entrée' , 'Date de sortie' , 'Motif']]
            for detention in detentions:
                detention_data.append([
                    str(detention.prison) ,
                    localtime(detention.start_date).strftime('%d/%m/%Y') ,
                    localtime(detention.end_date).strftime('%d/%m/%Y') if detention.end_date else 'En cours' ,
                    detention.reason
                ])

            detention_table = Table(detention_data , colWidths=[100 , 90 , 90 , 150])
            detention_table.setStyle(TableStyle([
                ('FONTNAME' , (0 , 0) , (-1 , -1) , 'Helvetica') ,
                ('FONTSIZE' , (0 , 0) , (-1 , -1) , 9) ,
                ('GRID' , (0 , 0) , (-1 , -1) , 1 , colors.black) ,
                ('BACKGROUND' , (0 , 0) , (-1 , 0) , colors.lightgrey) ,
                ('PADDING' , (0 , 0) , (-1 , -1) , 6) ,
            ]))
            elements.append(detention_table)
        else:
            elements.append(Paragraph("Aucune détention enregistrée" , styles['Normal']))

        # Générer le PDF
        doc.build(elements)

        # Préparer la réponse
        buffer.seek(0)
        response = HttpResponse(buffer.read() , content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="casier_judiciaire_{inmate.registration_number}.pdf"'

        return response


class ReleaseCertificatePDFView(LoginRequiredMixin , View):
    def get(self , request , pk):
        detention = get_object_or_404(Detention , pk=pk)
        if not detention.end_date:
            raise Http404("Ce détenu n'a pas encore été libéré")

        # Créer un buffer pour le PDF
        buffer = BytesIO()

        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer ,
            pagesize=A4 ,
            rightMargin=72 ,
            leftMargin=72 ,
            topMargin=72 ,
            bottomMargin=72
        )

        # Contenu du document
        elements = []
        styles = getSampleStyleSheet()

        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle' ,
            parent=styles['Heading1'] ,
            fontSize=16 ,
            spaceAfter=30 ,
            alignment=1
        )

        # Titre
        elements.append(Paragraph("Certificat de Libération" , title_style))
        elements.append(Spacer(1 , 20))

        # Contenu du certificat
        text = f"""
        Je soussigné(e), certifie que le détenu:

        Nom: {detention.inmate.last_name}
        Prénom: {detention.inmate.first_name}
        Numéro d'écrou: {detention.inmate.registration_number}

        a été libéré(e) de {detention.prison.name} le {localtime(detention.end_date).strftime('%d/%m/%Y')}.

        Cette libération fait suite à {detention.release_reason if detention.release_reason else 'la fin de sa peine'}.
        """

        elements.append(Paragraph(text , styles['Normal']))
        elements.append(Spacer(1 , 30))

        # Date et signature
        date_text = f"Fait à {detention.prison.city}, le {timezone.now().strftime('%d/%m/%Y')}"
        elements.append(Paragraph(date_text , styles['Normal']))
        elements.append(Spacer(1 , 60))
        elements.append(Paragraph("Signature et cachet:" , styles['Normal']))

        # Générer le PDF
        doc.build(elements)

        # Préparer la réponse
        buffer.seek(0)
        response = HttpResponse(buffer.read() , content_type='application/pdf')
        response[
            'Content-Disposition'] = f'attachment; filename="certificat_liberation_{detention.inmate.registration_number}.pdf"'

        return response


class InmateExportView(LoginRequiredMixin , View):
    def get(self , request , *args , **kwargs):
        format = request.GET.get('format' , 'excel')

        if format == 'excel':
            return self.export_excel()
        elif format == 'csv':
            return self.export_csv()

        return HttpResponse('Format non supporté' , status=400)

    def export_excel(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # En-têtes
        headers = ['ID' , 'Nom' , 'Prénom' , 'Date de naissance' , 'Nationalité' , 'Statut']
        for col , header in enumerate(headers):
            worksheet.write(0 , col , header)

        # Données
        inmates = Inmate.objects.all()
        for row , inmate in enumerate(inmates , 1):
            worksheet.write(row , 0 , inmate.id)
            worksheet.write(row , 1 , inmate.last_name)
            worksheet.write(row , 2 , inmate.first_name)
            worksheet.write(row , 3 , inmate.birth_date.strftime('%d/%m/%Y'))
            worksheet.write(row , 4 , inmate.nationality)
            worksheet.write(row , 5 , 'En détention' if inmate.is_active else 'Libéré')

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read() ,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=detenus.xlsx'
        return response

    def export_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=detenus.csv'

        writer = csv.writer(response)
        writer.writerow(['ID' , 'Nom' , 'Prénom' , 'Date de naissance' , 'Nationalité' , 'Statut'])

        inmates = Inmate.objects.all()
        for inmate in inmates:
            writer.writerow([
                inmate.id ,
                inmate.last_name ,
                inmate.first_name ,
                inmate.birth_date.strftime('%d/%m/%Y') ,
                inmate.nationality ,
                'En détention' if inmate.is_active else 'Libéré'
            ])

        return response

class CriminalRecordView(LoginRequiredMixin, DetailView):
    model = Inmate
    template_name = 'inmates/criminal_record.html'
    context_object_name = 'inmate'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detentions'] = self.object.get_criminal_record()
        context['prison'] = self.object.current_prison
        return context

class CriminalRecordPrintView(LoginRequiredMixin, DetailView):
    model = Inmate
    template_name = 'inmates/criminal_record_print.html'
    context_object_name = 'inmate'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detentions'] = self.object.get_criminal_record()
        context['prison'] = self.object.current_prison
        return context

class ReleaseCertificateView(LoginRequiredMixin, DetailView):
    model = Detention
    template_name = 'inmates/release_certificate.html'
    context_object_name = 'detention'

    def get_object(self):
        obj = super().get_object()
        if not obj.end_date:
            raise Http404("Ce détenu n'a pas encore été libéré")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prison'] = self.object.inmate.current_prison
        return context

class ReleaseCertificatePrintView(LoginRequiredMixin, DetailView):
    model = Detention
    template_name = 'inmates/release_certificate_print.html'
    context_object_name = 'detention'

    def get_object(self):
        obj = super().get_object()
        if not obj.end_date:
            raise Http404("Ce détenu n'a pas encore été libéré")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prison'] = self.object.inmate.current_prison
        return context

