# Generated by Django 4.2.22 on 2025-06-06 06:30

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inmates', '0005_visit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='visit',
            options={'ordering': ['-date'], 'permissions': [('can_approve_visit', 'Peut approuver les visites'), ('can_cancel_visit', 'Peut annuler les visites')], 'verbose_name': 'Visite', 'verbose_name_plural': 'Visites'},
        ),
        migrations.RemoveField(
            model_name='visit',
            name='approved',
        ),
        migrations.AddField(
            model_name='visit',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='visits_approved', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='visit',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='visit',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='visits_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='visit',
            name='status',
            field=models.CharField(choices=[('PLANIFIE', 'Planifiée'), ('CONFIRME', 'Confirmée'), ('TERMINE', 'Terminée'), ('ANNULE', 'Annulée')], default='PLANIFIE', max_length=20, verbose_name='Statut'),
        ),
        migrations.AddField(
            model_name='visit',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='visit',
            name='visitor_id_number',
            field=models.CharField(default='ID-00000', max_length=20, verbose_name="Numéro d'identification"),
        ),
        migrations.AddField(
            model_name='visit',
            name='visitor_phone',
            field=models.CharField(default='0000000000', max_length=15, verbose_name='Téléphone'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date et heure de la visite'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(seconds=3600), verbose_name='Durée prévue'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='inmate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visits', to='inmates.inmate', verbose_name='Détenu'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='notes',
            field=models.TextField(blank=True, default='', verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='visitor_name',
            field=models.CharField(default='Visiteur', max_length=100, verbose_name='Nom du visiteur'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='visitor_relation',
            field=models.CharField(choices=[('FAMILLE', 'Famille'), ('CONJOINT', 'Conjoint(e)'), ('AMI', 'Ami(e)'), ('AVOCAT', 'Avocat'), ('AUTRE', 'Autre')], default='AUTRE', max_length=20, verbose_name='Relation avec le détenu'),
        ),
    ]
