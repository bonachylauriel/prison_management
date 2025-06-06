from django.contrib import admin
from django.utils.html import format_html
from .models import Inmate, Detention, Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['visitor_name' , 'inmate' , 'date' , 'status']
    list_filter = ['status' , 'date']
    search_fields = ['visitor_name' , 'visitor_id_number' , 'inmate__first_name' , 'inmate__last_name']

    def has_add_permission(self , request):
        return True

    def has_change_permission(self , request , obj=None):
        return True

    def has_delete_permission(self , request , obj=None):
        return True


@admin.register(Inmate)
class InmateAdmin(admin.ModelAdmin):
    list_display = ('get_photo_thumbnail', 'registration_number', 'first_name', 'last_name', 'current_prison')
    list_filter = ('current_prison', 'gender', 'is_recidivist')
    search_fields = ('registration_number', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'get_photo_preview')

    def get_photo_thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)
        return "Pas de photo"
    get_photo_thumbnail.short_description = "Photo"

    def get_photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="200" />', obj.photo.url)
        return "Pas de photo"
    get_photo_preview.short_description = "Aperçu photo"

@admin.register(Detention)
class DetentionAdmin(admin.ModelAdmin):
    list_display = ('inmate', 'start_date', 'end_date', 'magistrate')
    list_filter = ('magistrate',)
    search_fields = ('inmate__registration_number', 'inmate__first_name', 'inmate__last_name')