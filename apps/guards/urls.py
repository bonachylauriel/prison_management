from django.urls import path
from . import views

app_name = 'guards'

urlpatterns = [
    path('', views.GuardListView.as_view(), name='guard_list'),
    path('create/', views.GuardCreateView.as_view(), name='guard_create'),
    path('<int:pk>/', views.GuardDetailView.as_view(), name='guard_detail'),
    path('<int:pk>/update/', views.GuardUpdateView.as_view(), name='guard_update'),
    path('shifts/', views.ShiftListView.as_view(), name='shift_list'),
    path('shifts/create/', views.ShiftCreateView.as_view(), name='shift_create'),
    path('shifts/<int:pk>/update/', views.ShiftUpdateView.as_view(), name='shift_update'),
    # Gardes
    # Équipes
    path('teams/' , views.TeamUnitListView.as_view() , name='team_list') ,
    path('teams/create/' , views.TeamUnitCreateView.as_view() , name='team_create') ,
    path('teams/<int:pk>/update/' , views.TeamUnitUpdateView.as_view() , name='team_update') ,

    # Plannings
    path('schedules/' , views.ScheduleListView.as_view() , name='schedule_list') ,
    path('schedules/create/' , views.ScheduleCreateView.as_view() , name='schedule_create') ,

    # Incidents
    path('incidents/' , views.IncidentReportListView.as_view() , name='incident_list') ,
    path('incidents/create/' , views.IncidentReportCreateView.as_view() , name='incident_create') ,
    path('incidents/<int:pk>/update/' , views.IncidentReportUpdateView.as_view() , name='incident_update') ,

    # Services
    path('shifts/create/' , views.GuardShiftCreateView.as_view() , name='shift_create') ,
    path('profile/', views.GuardProfileView.as_view(), name='profile'),

]