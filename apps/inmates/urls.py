from django.urls import path
from . import views

app_name = 'inmates'

urlpatterns = [
    path('', views.InmateListView.as_view(), name='inmate_list'),
    path('<int:pk>/', views.InmateDetailView.as_view(), name='inmate_detail'),
    path('create/', views.InmateCreateView.as_view(), name='inmate_create'),
    path('<int:pk>/update/', views.InmateUpdateView.as_view(), name='inmate_update'),
    path('<int:pk>/delete/', views.InmateDeleteView.as_view(), name='inmate_delete'),
    path('visits/network/', views.VisitNetworkView.as_view(), name='visit_network'),
    path('visits/network/data/<str:prison_id>/', views.VisitNetworkView.as_view(), name='visit_network_data'),
    path('visits/' , views.VisitListView.as_view() , name='visit_list') ,
    path('inmate/<int:inmate_id>/visit/add/' , views.VisitCreateView.as_view() , name='visit_create') ,
    path('visit/<int:pk>/edit/' , views.VisitUpdateView.as_view() , name='visit_update') ,
    path('visit/<int:pk>/delete/' , views.VisitDeleteView.as_view() , name='visit_delete') ,
    path('visit/<int:pk>/approve/' , views.VisitApprovalView.as_view() , name='visit_approve') ,

]
