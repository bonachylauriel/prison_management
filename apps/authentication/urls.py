from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'

urlpatterns = [
    # Login et Logout
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='authentication:login'), name='logout'),

    # Inscription et profil
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),

    # Changement de mot de passe (utilisateur connecté)
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='authentication/password_change_done.html'
         ),
         name='password_change_done'),

    # Réinitialisation de mot de passe (utilisateur non connecté)
    path('password/reset/',
         auth_views.PasswordResetView.as_view(
             template_name='authentication/password_reset_form.html',
             email_template_name='authentication/password_reset_email.html',
             subject_template_name='authentication/password_reset_subject.txt',
             form_class=views.CustomPasswordResetForm,
             success_url='/authentication/password/reset/done/'
         ),
         name='password_reset'),

    path('password/reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='authentication/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='authentication/password_reset_confirm.html',
             success_url='/authentication/password/reset/complete/'
         ),
         name='password_reset_confirm'),

    path('password/reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='authentication/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]