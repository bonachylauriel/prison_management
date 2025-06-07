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
    # ... autres URLs existantes ...
    path('statistics/' , views.InmateStatisticsView.as_view() , name='statistics') ,
    path('export/' , views.InmateExportView.as_view() , name='export') ,
    path('<int:pk>/criminal-record/pdf/' , views.CriminalRecordPDFView.as_view() , name='criminal_record_pdf') ,
    path('detention/<int:detention_id>/release-certificate/pdf/' ,
         views.ReleaseCertificatePDFView.as_view() , name='release_certificate_pdf') ,
# URLs pour les documents des détenus
    path('inmates/<int:pk>/criminal-record/', views.CriminalRecordView.as_view(), name='criminal_record'),
    path('inmates/<int:pk>/criminal-record/pdf/', views.CriminalRecordPDFView.as_view(), name='criminal_record_pdf'),
    path('inmates/<int:pk>/criminal-record/print/', views.CriminalRecordPrintView.as_view(), name='criminal_record_print'),
# URLs pour les documents de détention
    # URLs pour le casier judiciaire
    path('inmate/<int:pk>/criminal-record/' ,views.CriminalRecordView.as_view() ,name='criminal_record') ,
    path('inmate/<int:pk>/criminal-record/print/' ,views.CriminalRecordPrintView.as_view() ,name='criminal_record_print') ,
    path('inmate/<int:pk>/criminal-record/pdf/' , views.CriminalRecordPDFView.as_view() ,name='criminal_record_pdf') ,

    # URLs pour le certificat de libération
    path('detention/<int:pk>/release-certificate/' ,views.ReleaseCertificateView.as_view() ,name='release_certificate') ,
    path('detention/<int:pk>/release-certificate/print/' ,
         views.ReleaseCertificatePrintView.as_view() ,name='release_certificate_print') ,
    path('detention/<int:pk>/release-certificate/pdf/' ,
         views.ReleaseCertificatePDFView.as_view() ,name='release_certificate_pdf') ,
    path('<int:pk>/criminal-record/pdf/', views.CriminalRecordPDFView.as_view(), name='criminal_record_pdf'),
    path('detention/<int:pk>/release-certificate/pdf/', views.ReleaseCertificatePDFView.as_view(), name='release_certificate_pdf'),
]
