# Generated by Django 4.2.22 on 2025-06-06 03:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prisons', '0002_alter_prison_options_prison_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrisonConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('established_date', models.DateField(auto_now_add=True, verbose_name="Date d'établissement")),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('max_transfer_capacity', models.PositiveIntegerField(help_text='Nombre maximum de détenus pouvant être transférés simultanément', verbose_name='Capacité maximale de transfert')),
                ('distance_km', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Distance (km)')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('prison_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections_from', to='prisons.prison', verbose_name='Prison de départ')),
                ('prison_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections_to', to='prisons.prison', verbose_name="Prison d'arrivée")),
            ],
            options={
                'verbose_name': 'Connexion entre prisons',
                'verbose_name_plural': 'Connexions entre prisons',
                'unique_together': {('prison_from', 'prison_to')},
            },
        ),
        migrations.CreateModel(
            name='TransferLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_date', models.DateTimeField(auto_now_add=True, verbose_name='Date de transfert')),
                ('number_of_inmates', models.PositiveIntegerField(verbose_name='Nombre de détenus')),
                ('success', models.BooleanField(default=True, verbose_name='Succès')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='prisons.prisonconnection', verbose_name='Connexion')),
            ],
            options={
                'verbose_name': 'Journal de transfert',
                'verbose_name_plural': 'Journal des transferts',
            },
        ),
        migrations.AddField(
            model_name='prison',
            name='connected_prisons',
            field=models.ManyToManyField(related_name='connected_to', through='prisons.PrisonConnection', to='prisons.prison', verbose_name='Prisons connectées'),
        ),
    ]
