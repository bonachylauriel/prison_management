from django.urls import path
from . import views

app_name = 'prisons'

urlpatterns = [
    path('' , views.PrisonDashboardView.as_view() , name='dashboard') ,
    path('list/' , views.PrisonListView.as_view() , name='list') ,
    path('<int:pk>/' , views.PrisonDetailView.as_view() , name='detail') ,
    path('create/' , views.PrisonCreateView.as_view() , name='create') ,
    path('<int:pk>/update/' , views.PrisonUpdateView.as_view() , name='update') ,
    path('<int:pk>/delete/' , views.PrisonDeleteView.as_view() , name='delete') ,
    path('transfer/', views.TransferManagementView.as_view(), name='transfer_management'),
    path('get-inmates/<int:prison_id>/', views.PrisonInmatesView.as_view(), name='get_inmates'),
    path('get-connections/<int:prison_id>/', views.PrisonConnectionsView.as_view(), name='get_connections'),
    path('process-transfer/', views.ProcessTransferView.as_view(), name='process_transfer'),
    path('grid/', views.PrisonGridView.as_view(), name='grid'),


]