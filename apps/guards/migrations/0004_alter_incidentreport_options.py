# Generated by Django 5.0 on 2025-06-06 01:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('guards', '0003_incidentreport_reporter_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incidentreport',
            options={'ordering': ['-incident_date'], 'permissions': [('can_close_incident', 'Peut clôturer un incident'), ('can_view_all_incidents', 'Peut voir tous les incidents'), ('can_export_incidents', 'Peut exporter les incidents')], 'verbose_name': "Rapport d'incident", 'verbose_name_plural': "Rapports d'incidents"},
        ),
    ]
