# Generated by Django 5.0 on 2025-06-05 16:48

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inmates', '0002_detention_created_at_detention_updated_at_and_more'),
        ('prisons', '0002_alter_prison_options_prison_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inmate',
            options={'ordering': ['-admission_date'], 'verbose_name': 'Détenu', 'verbose_name_plural': 'Détenus'},
        ),
        migrations.AlterField(
            model_name='inmate',
            name='admission_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date d'admission"),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='crime_description',
            field=models.TextField(verbose_name='Description du crime'),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='current_prison',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='prisons.prison', verbose_name='Prison actuelle'),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='date_of_birth',
            field=models.DateField(verbose_name='Date de naissance'),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='first_name',
            field=models.CharField(max_length=100, verbose_name='Prénom'),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='gender',
            field=models.CharField(choices=[('M', 'Masculin'), ('F', 'Féminin')], max_length=1, verbose_name='Genre'),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='health_status',
            field=models.TextField(verbose_name='État de santé'),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='is_recidivist',
            field=models.BooleanField(default=False, verbose_name='Récidiviste'),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='last_name',
            field=models.CharField(max_length=100, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='photo',
            field=models.ImageField(blank=True, help_text='Format accepté : JPG, JPEG, PNG', null=True, upload_to='inmates_photos/%Y/%m/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])], verbose_name='Photo'),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='registration_number',
            field=models.CharField(max_length=20, unique=True, verbose_name="Numéro d'écrou"),
        ),
        migrations.AlterField(
            model_name='inmate',
            name='release_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date de libération'),
        ),
        migrations.DeleteModel(
            name='Detention',
        ),
    ]
