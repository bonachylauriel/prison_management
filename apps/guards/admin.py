from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import render
from django.db.models import Count
from django.core.cache import cache
from django.utils import timezone
from .models import User , GuardSpecialization , GuardCertification , GuardShift , TeamUnit , Schedule , IncidentReport


class RankFilter(admin.SimpleListFilter):
    title = 'Grade'
    parameter_name = 'rank_level'

    def lookups(self , request , model_admin):
        return User.RANK_CHOICES

    def queryset(self , request , queryset):
        if self.value():
            return queryset.filter(rank=self.value())


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('badge_number' , 'get_full_name' , 'rank' , 'prison' , 'is_on_duty' , 'get_photo' ,
                    'action_buttons')
    list_filter = (RankFilter , 'prison' , 'is_on_duty' , 'is_active' , 'current_shift')
    search_fields = ('first_name' , 'last_name' , 'badge_number' , 'email')
    ordering = ('last_name' , 'first_name')
    actions = ['mark_on_duty' , 'mark_off_duty' , 'export_selected_guards']

    fieldsets = (
        ('Informations personnelles' , {
            'fields': (('first_name' , 'last_name') , 'email' , 'phone' ,
                       'badge_number' , 'date_of_birth' , 'address' , 'photo')
        }) ,
        ('Informations professionnelles' , {
            'fields': (('rank' , 'prison') , ('current_shift' , 'is_on_duty') ,
                       'hire_date' , 'current_team')
        }) ,
        ('Qualifications' , {
            'fields': ('specializations' , 'certifications') ,
            'classes': ('collapse' ,)
        }) ,
        ('Permissions' , {
            'fields': ('is_active' , 'is_staff' , 'is_superuser' , 'groups' , 'user_permissions') ,
            'classes': ('collapse' ,)
        }) ,
    )

    def get_photo(self , obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />' , obj.photo.url)
        return format_html('<span class="badge badge-warning">Aucune photo</span>')

    get_photo.short_description = "Photo"

    def action_buttons(self , obj):
        return format_html(
            '<a class="button btn btn-info btn-sm" href="{}">Planning</a>&nbsp;'
            '<a class="button btn btn-warning btn-sm" href="{}">Incidents</a>' ,
            reverse('admin:guards_schedule_changelist') + f'?guard={obj.id}' ,
            reverse('admin:guards_incidentreport_changelist') + f'?reporting_guard={obj.id}'
        )

    action_buttons.short_description = 'Actions rapides'

    def mark_on_duty(self , request , queryset):
        updated = queryset.update(is_on_duty=True)
        self.message_user(request , f'{updated} garde(s) marqué(s) en service.')

    mark_on_duty.short_description = "Marquer les gardes sélectionnés en service"

    def mark_off_duty(self , request , queryset):
        updated = queryset.update(is_on_duty=False)
        self.message_user(request , f'{updated} garde(s) marqué(s) hors service.')

    mark_off_duty.short_description = "Marquer les gardes sélectionnés hors service"

    def export_selected_guards(self , request , queryset):
        # Logique d'export à implémenter
        pass

    export_selected_guards.short_description = "Exporter les gardes sélectionnés"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/' , self.admin_site.admin_view(self.dashboard_view) , name='guards_dashboard') ,
        ]
        return custom_urls + urls

    def dashboard_view(self , request):
        context = {
            'guards_count': User.objects.count() ,
            'on_duty_count': User.objects.filter(is_on_duty=True).count() ,
            'incidents_open': IncidentReport.objects.filter(status='OPEN').count() ,
            'teams_active': TeamUnit.objects.filter(is_active=True).count() ,
            'recent_incidents': IncidentReport.objects.order_by('-incident_date')[:5] ,
            'title': "Tableau de bord des gardes" ,
            'subtitle': "Vue d'ensemble du système"
        }
        return render(request , 'admin/guards/dashboard.html' , context)


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('title' , 'incident_date' , 'severity' , 'status' , 'location' , 'get_status_badge')
    list_filter = ('status' , 'severity' , 'incident_date')
    search_fields = ('title' , 'description' , 'location')
    date_hierarchy = 'incident_date'
    actions = ['mark_resolved' , 'mark_investigating' , 'export_as_pdf' , 'escalate_incident']

    readonly_fields = ('created_at' , 'updated_at')

    fieldsets = (
        ('Informations principales' , {
            'fields': (('title' , 'incident_date') , 'location' ,
                       ('severity' , 'status') , 'description')
        }) ,
        ('Personnes impliquées' , {
            'fields': ('reporter' , 'reporting_guard' , 'involved_guards' ,
                       'involved_inmates' , 'witnesses')
        }) ,
        ('Actions et suivi' , {
            'fields': ('immediate_action' , 'follow_up_action' , 'attachments')
        }) ,
        ('Clôture' , {
            'fields': (('closed_at' , 'closed_by') , ('created_at' , 'updated_at')) ,
            'classes': ('collapse' ,)
        }) ,
    )

    def get_status_badge(self , obj):
        colors = {
            'OPEN': 'danger' ,
            'INVESTIGATING': 'warning' ,
            'RESOLVED': 'success' ,
            'CLOSED': 'secondary'
        }
        return format_html('<span class="badge badge-{}">{}</span>' ,
                           colors.get(obj.status , 'primary') ,
                           obj.get_status_display())

    get_status_badge.short_description = 'Statut'

    def mark_resolved(self , request , queryset):
        updated = queryset.update(status='RESOLVED')
        self.message_user(request , f'{updated} incident(s) marqué(s) comme résolu(s).')

    mark_resolved.short_description = "Marquer comme résolu"

    def mark_investigating(self , request , queryset):
        updated = queryset.update(status='INVESTIGATING')
        self.message_user(request , f'{updated} incident(s) marqué(s) en cours d\'investigation.')

    mark_investigating.short_description = "Marquer en investigation"

    def export_as_pdf(self , request , queryset):
        # Logique d'export PDF à implémenter
        pass

    export_as_pdf.short_description = "Exporter en PDF"

    def escalate_incident(self , request , queryset):
        # Logique d'escalade à implémenter
        pass

    escalate_incident.short_description = "Escalader l'incident"


@admin.register(TeamUnit)
class TeamUnitAdmin(admin.ModelAdmin):
    list_display = ('name' , 'prison' , 'leader' , 'is_active' , 'get_members_count' , 'get_team_status')
    list_filter = ('prison' , 'is_active')
    search_fields = ('name' , 'leader__first_name' , 'leader__last_name')
    actions = ['activate_teams' , 'deactivate_teams']

    def get_members_count(self , obj):
        count = obj.members.count()
        return format_html('<span class="badge badge-info">{}</span>' , count)

    get_members_count.short_description = "Effectif"

    def get_team_status(self , obj):
        return format_html('<span class="badge badge-{}">{}</span>' ,
                           'success' if obj.is_active else 'danger' ,
                           'Active' if obj.is_active else 'Inactive')

    get_team_status.short_description = "Statut"

    def activate_teams(self , request , queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request , f'{updated} équipe(s) activée(s).')

    activate_teams.short_description = "Activer les équipes sélectionnées"

    def deactivate_teams(self , request , queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request , f'{updated} équipe(s) désactivée(s).')

    deactivate_teams.short_description = "Désactiver les équipes sélectionnées"


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('guard' , 'team' , 'start_date' , 'end_date' , 'rotation_pattern' , 'is_active' , 'get_duration')
    list_filter = ('is_active' , 'rotation_pattern' , 'team')
    search_fields = ('guard__first_name' , 'guard__last_name' , 'notes')
    date_hierarchy = 'start_date'
    actions = ['activate_schedules' , 'deactivate_schedules']

    def get_duration(self , obj):
        duration = (obj.end_date - obj.start_date).days
        return f"{duration} jours"

    get_duration.short_description = "Durée"


@admin.register(GuardShift)
class GuardShiftAdmin(admin.ModelAdmin):
    list_display = ('guard' , 'start_time' , 'end_time' , 'area' , 'is_completed' , 'get_shift_duration')
    list_filter = ('is_completed' , 'area')
    search_fields = ('guard__first_name' , 'guard__last_name' , 'notes')
    date_hierarchy = 'start_time'
    actions = ['mark_completed' , 'mark_incomplete']

    def get_shift_duration(self , obj):
        duration = obj.end_time - obj.start_time
        hours = duration.total_seconds() / 3600
        return f"{hours:.1f} heures"

    get_shift_duration.short_description = "Durée"


@admin.register(GuardSpecialization)
class GuardSpecializationAdmin(admin.ModelAdmin):
    list_display = ('name' , 'get_guards_count' , 'description')
    search_fields = ('name' , 'description')

    def get_guards_count(self , obj):
        count = obj.specialized_guards.count()
        return format_html('<span class="badge badge-primary">{}</span>' , count)

    get_guards_count.short_description = "Nombre de gardes"


@admin.register(GuardCertification)
class GuardCertificationAdmin(admin.ModelAdmin):
    list_display = ('name' , 'issuing_authority' , 'validity_period' , 'get_certified_guards')
    search_fields = ('name' , 'issuing_authority')

    def get_certified_guards(self , obj):
        return obj.certified_guards.count()

    get_certified_guards.short_description = "Gardes certifiés"


# Personnalisation du site d'administration
admin.site.site_header = "Administration du Système Pénitentiaire"
admin.site.site_title = "Administration Prison"
admin.site.index_title = "Tableau de bord"