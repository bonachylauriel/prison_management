from django.contrib import admin
from .models import Prison , PrisonConnection , TransferLog


class PrisonConnectionInline(admin.TabularInline):
    model = PrisonConnection
    fk_name = 'prison_from'
    extra = 1
    fields = ['prison_to' , 'is_active' , 'max_transfer_capacity' , 'distance_km' , 'notes']


class TransferLogInline(admin.TabularInline):
    model = TransferLog
    extra = 0
    readonly_fields = ['transfer_date']
    fields = ['number_of_inmates' , 'success' , 'notes']
    can_delete = False


@admin.register(Prison)
class PrisonAdmin(admin.ModelAdmin):
    list_display = (
        'name' ,
        'province' ,
        'capacity' ,
        'current_population' ,
        'get_occupation_rate' ,
        'get_connection_count'
    )
    list_filter = ('province' , 'connections_from__is_active')
    search_fields = ('name' , 'province')
    inlines = [PrisonConnectionInline]

    def get_occupation_rate(self , obj):
        return f"{obj.get_occupation_rate():.1f}%"

    get_occupation_rate.short_description = "Taux d'occupation"

    def get_connection_count(self , obj):
        return obj.connected_prisons.count()

    get_connection_count.short_description = "Prisons connectées"

    class Media:
        css = {
            'all': ('css/admin/prison.css' ,)
        }
        js = ('js/admin/prison.js' ,)

    def save_model(self , request , obj , form , change):
        if not change:  # Si c'est une création
            obj.created_by = request.user
        obj.save()


@admin.register(PrisonConnection)
class PrisonConnectionAdmin(admin.ModelAdmin):
    list_display = (
        'prison_from' ,
        'prison_to' ,
        'is_active' ,
        'max_transfer_capacity' ,
        'distance_km' ,
        'established_date'
    )
    list_filter = (
        'is_active' ,
        'prison_from__province' ,
        'prison_to__province' ,
        'established_date'
    )
    search_fields = (
        'prison_from__name' ,
        'prison_to__name' ,
        'notes'
    )
    inlines = [TransferLogInline]
    fieldsets = (
        ('Informations de base' , {
            'fields': (
                ('prison_from' , 'prison_to') ,
                'is_active'
            )
        }) ,
        ('Détails du transfert' , {
            'fields': (
                'max_transfer_capacity' ,
                'distance_km' ,
                'notes'
            )
        }) ,
    )


@admin.register(TransferLog)
class TransferLogAdmin(admin.ModelAdmin):
    list_display = (
        'connection' ,
        'transfer_date' ,
        'number_of_inmates' ,
        'success'
    )
    list_filter = (
        'success' ,
        'transfer_date' ,
        'connection__prison_from' ,
        'connection__prison_to'
    )
    readonly_fields = ['transfer_date']
    search_fields = (
        'connection__prison_from__name' ,
        'connection__prison_to__name' ,
        'notes'
    )
    date_hierarchy = 'transfer_date'

    fieldsets = (
        ('Informations de transfert' , {
            'fields': (
                'connection' ,
                'transfer_date' ,
                'number_of_inmates' ,
                'success'
            )
        }) ,
        ('Notes' , {
            'fields': ('notes' ,) ,
            'classes': ('collapse' ,)
        }) ,
    )

    def has_add_permission(self , request):
        return True

    def has_delete_permission(self , request , obj=None):
        # Empêcher la suppression des logs de transfert
        return False