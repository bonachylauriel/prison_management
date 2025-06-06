from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm , CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('username' , 'email' , 'role' , 'is_staff' , 'is_active')
    list_filter = ('role' , 'is_staff' , 'is_active')

    fieldsets = (
        (None , {'fields': ('username' , 'email' , 'password')}) ,
        ('Informations personnelles' ,
         {'fields': ('first_name' , 'last_name' , 'role' , 'phone_number' , 'profile_photo')}) ,
        ('Permissions' , {'fields': ('is_active' , 'is_staff' , 'is_superuser' , 'groups' , 'user_permissions')}) ,
        ('Sécurité' , {'fields': ('two_factor_enabled' , 'last_login_ip')}) ,
    )

    add_fieldsets = (
        (None , {
            'classes': ('wide' ,) ,
            'fields': ('username' , 'email' , 'password1' , 'password2' , 'role' , 'is_staff' , 'is_active')}
         ) ,
    )

    search_fields = ('email' , 'username')
    ordering = ('email' ,)


admin.site.register(User , CustomUserAdmin)