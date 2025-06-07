from django.urls import path
from . import views

app_name = 'magistrates'

urlpatterns = [
    path('', views.MagistrateListView.as_view(), name='magistrate_list'),
    path('<int:pk>/', views.MagistrateDetailView.as_view(), name='magistrate_detail'),
    path('create/', views.MagistrateCreateView.as_view(), name='magistrate_create'),
    path('<int:pk>/update/', views.MagistrateUpdateView.as_view(), name='magistrate_update'),
    path('<int:pk>/delete/', views.MagistrateDeleteView.as_view(), name='magistrate_delete'),
    path('<int:pk>/profile/', views.MagistrateProfileView.as_view(), name='magistrate_profile'),

]