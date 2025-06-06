from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from apps.prisons.models import Prison
from django.conf import settings


class User(AbstractUser):
    photo = models.ImageField(upload_to='guards/photos/' , null=True , blank=True)
    phone_number = models.CharField(max_length=15 , blank=True)

    RANK_CHOICES = [
        ('TRAINEE' , 'Stagiaire') ,
        ('GUARD' , 'Gardien') ,
        ('SENIOR' , 'Gardien Principal') ,
        ('CHIEF' , 'Chef de Service') ,
        ('SUPERVISOR' , 'Superviseur') ,
    ]

    SHIFT_CHOICES = [
        ('MORNING' , 'Matin (6h-14h)') ,
        ('AFTERNOON' , 'Après-midi (14h-22h)') ,
        ('NIGHT' , 'Nuit (22h-6h)') ,
    ]

    # Informations personnelles
    phone = models.CharField(max_length=20 , blank=True , verbose_name="Téléphone")
    badge_number = models.CharField(max_length=20 , unique=True , blank=True , null=True ,
                                    verbose_name="Numéro de badge")
    date_of_birth = models.DateField(null=True , blank=True , verbose_name="Date de naissance")
    address = models.TextField(blank=True , verbose_name="Adresse")
    photo = models.ImageField(
        upload_to='guards_photos/%Y/%m/' ,
        verbose_name="Photo" ,
        null=True ,
        blank=True
    )

    # Informations professionnelles
    rank = models.CharField(
        max_length=20 ,
        choices=RANK_CHOICES ,
        default='GUARD' ,
        verbose_name="Grade"
    )
    prison = models.ForeignKey(
        Prison ,
        on_delete=models.PROTECT ,
        related_name='guards' ,
        null=True ,
        blank=True ,
        verbose_name="Prison assignée"
    )
    current_shift = models.CharField(
        max_length=20 ,
        choices=SHIFT_CHOICES ,
        null=True ,
        blank=True ,
        verbose_name="Service actuel"
    )
    hire_date = models.DateField(
        default=timezone.now ,
        verbose_name="Date d'embauche"
    )
    is_on_duty = models.BooleanField(
        default=False ,
        verbose_name="En service"
    )

    # Spécialisations et certifications
    specializations = models.ManyToManyField(
        'GuardSpecialization' ,
        blank=True ,
        related_name='specialized_guards' ,
        verbose_name="Spécialisations"
    )
    certifications = models.ManyToManyField(
        'GuardCertification' ,
        blank=True ,
        related_name='certified_guards' ,
        verbose_name="Certifications"
    )

    # Relations avec les équipes et plannings
    current_team = models.ForeignKey(
        'TeamUnit' ,
        on_delete=models.SET_NULL ,
        null=True ,
        blank=True ,
        related_name='current_members' ,
        verbose_name="Équipe actuelle"
    )

    # Relations avec auth.Group et auth.Permission
    groups = models.ManyToManyField(
        'auth.Group' ,
        related_name='guard_user_groups' ,
        blank=True ,
        help_text='The groups this user belongs to.' ,
        verbose_name='groups' ,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission' ,
        related_name='guard_user_permissions' ,
        blank=True ,
        help_text='Specific permissions for this user.' ,
        verbose_name='user permissions' ,
    )

    class Meta:
        verbose_name = "Garde"
        verbose_name_plural = "Gardes"

    def __str__(self):
        return f"{self.badge_number} - {self.get_full_name()}"


class GuardSpecialization(models.Model):
    name = models.CharField(max_length=100 , verbose_name="Nom")
    description = models.TextField(verbose_name="Description")

    class Meta:
        verbose_name = "Spécialisation"
        verbose_name_plural = "Spécialisations"

    def __str__(self):
        return self.name


class GuardCertification(models.Model):
    name = models.CharField(max_length=100 , verbose_name="Nom")
    issuing_authority = models.CharField(max_length=200 , verbose_name="Autorité émettrice")
    validity_period = models.IntegerField(verbose_name="Période de validité (mois)")

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"

    def __str__(self):
        return self.name


class GuardShift(models.Model):
    guard = models.ForeignKey(User , on_delete=models.CASCADE , related_name='shifts' , verbose_name="Garde")
    start_time = models.DateTimeField(verbose_name="Début du service")
    end_time = models.DateTimeField(verbose_name="Fin du service")
    area = models.CharField(max_length=100 , verbose_name="Zone assignée")
    notes = models.TextField(blank=True , verbose_name="Notes")
    is_completed = models.BooleanField(default=False , verbose_name="Service terminé")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['-start_time']

    def __str__(self):
        return f"Service de {self.guard.get_full_name()} le {self.start_time.strftime('%d/%m/%Y')}"


class TeamUnit(models.Model):
    """Unité/Équipe de gardes"""
    name = models.CharField(max_length=100 , verbose_name="Nom de l'équipe")
    leader = models.ForeignKey(
        User ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='led_teams' ,
        verbose_name="Chef d'équipe"
    )
    members = models.ManyToManyField(
        User ,
        related_name='team_memberships' ,
        verbose_name="Membres"
    )
    prison = models.ForeignKey(
        Prison ,
        on_delete=models.PROTECT ,
        related_name='teams' ,
        verbose_name="Prison"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True , verbose_name="Équipe active")

    class Meta:
        verbose_name = "Unité"
        verbose_name_plural = "Unités"
        unique_together = ['name' , 'prison']

    def __str__(self):
        return f"Unité {self.name} - {self.prison}"


class Schedule(models.Model):
    """Planning des gardes"""
    ROTATION_PATTERNS = [
        ('2X2' , '2 jours travail / 2 jours repos') ,
        ('3X2' , '3 jours travail / 2 jours repos') ,
        ('4X4' , '4 jours travail / 4 jours repos') ,
        ('5X2' , '5 jours travail / 2 jours repos') ,
        ('7X7' , '7 jours travail / 7 jours repos') ,
    ]

    guard = models.ForeignKey(
        User ,
        on_delete=models.CASCADE ,
        related_name='schedules' ,
        verbose_name="Garde"
    )
    team = models.ForeignKey(
        TeamUnit ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='team_schedules' ,
        verbose_name="Unité"
    )
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    rotation_pattern = models.CharField(
        max_length=50 ,
        choices=ROTATION_PATTERNS ,
        verbose_name="Pattern de rotation"
    )
    shifts = models.ManyToManyField(
        GuardShift ,
        related_name='schedule_shifts' ,
        blank=True ,
        verbose_name="Services planifiés"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True , verbose_name="Notes")
    is_active = models.BooleanField(default=True , verbose_name="Planning actif")

    class Meta:
        verbose_name = "Planning"
        verbose_name_plural = "Plannings"
        ordering = ['-start_date']

    def __str__(self):
        return f"Planning de {self.guard.get_full_name()} ({self.start_date} - {self.end_date})"


class IncidentReport(models.Model):
    """Rapports d'incidents"""
    SEVERITY_CHOICES = [
        ('LOW' , 'Faible') ,
        ('MEDIUM' , 'Moyen') ,
        ('HIGH' , 'Élevé') ,
        ('CRITICAL' , 'Critique') ,
    ]

    STATUS_CHOICES = [
        ('OPEN' , 'Ouvert') ,
        ('INVESTIGATING' , 'En cours d\'investigation') ,
        ('RESOLVED' , 'Résolu') ,
        ('CLOSED' , 'Fermé') ,
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL ,
        on_delete=models.CASCADE ,
        related_name='user_reported_incidents' ,
        verbose_name="Rapporteur",
        null=True ,  # Ajout de cette ligne
        blank=True ,  # Ajout de cette ligne
        default=None  # Ajout de cette ligne
    )

    title = models.CharField(max_length=200 , verbose_name="Titre")
    incident_date = models.DateTimeField(verbose_name="Date et heure de l'incident")
    location = models.CharField(max_length=100 , verbose_name="Lieu")
    severity = models.CharField(
        max_length=10 ,
        choices=SEVERITY_CHOICES ,
        verbose_name="Gravité"
    )

    description = models.TextField(verbose_name="Description")
    reporting_guard = models.ForeignKey(
        User ,
        on_delete=models.PROTECT ,
        related_name='guard_reported_incidents' ,
        verbose_name="Garde rapporteur"
    )
    involved_inmates = models.ManyToManyField(
        'inmates.Inmate' ,
        blank=True ,
        related_name='involved_incidents' ,
        verbose_name="Détenus impliqués"
    )
    involved_guards = models.ManyToManyField(
        User ,
        related_name='involved_incidents' ,
        blank=True ,
        verbose_name="Gardes impliqués"
    )
    witnesses = models.ManyToManyField(
        User ,
        related_name='witnessed_incidents' ,
        blank=True ,
        verbose_name="Témoins"
    )
    immediate_action = models.TextField(verbose_name="Actions immédiates prises")
    follow_up_action = models.TextField(blank=True , verbose_name="Actions de suivi")
    status = models.CharField(
        max_length=20 ,
        choices=STATUS_CHOICES ,
        default='OPEN' ,
        verbose_name="Statut"
    )
    attachments = models.FileField(
        upload_to='incident_reports/%Y/%m/' ,
        blank=True ,
        null=True ,
        verbose_name="Pièces jointes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True , blank=True)
    closed_by = models.ForeignKey(
        User ,
        on_delete=models.SET_NULL ,
        null=True ,
        blank=True ,
        related_name='closed_incidents' ,
        verbose_name="Fermé par"
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.closed_at and not self.closed_by:
            raise ValidationError("Un incident ne peut pas être clôturé sans spécifier qui l'a clôturé.")
        if self.status == 'CLOSED' and not self.closed_at:
            raise ValidationError("Un incident marqué comme fermé doit avoir une date de clôture.")

    def save(self , *args , **kwargs):
        if self.status == 'CLOSED' and not self.closed_at:
            self.closed_at = timezone.now()
        super().save(*args , **kwargs)

    def get_duration(self):
        """Retourne la durée depuis la création de l'incident"""
        if self.closed_at:
            return self.closed_at - self.created_at
        return timezone.now() - self.created_at

    @property
    def is_closed(self):
        """Vérifie si l'incident est clôturé"""
        return self.status == 'CLOSED'

    @property
    def needs_attention(self):
        """Vérifie si l'incident nécessite une attention particulière"""
        return (
            self.severity in ['HIGH', 'CRITICAL'] and
            self.status not in ['RESOLVED', 'CLOSED']
        )

    class Meta:
        verbose_name = "Rapport d'incident"
        verbose_name_plural = "Rapports d'incidents"
        ordering = ['-incident_date']
        permissions = [
            ("can_close_incident" , "Peut clôturer un incident") ,
            ("can_view_all_incidents" , "Peut voir tous les incidents") ,
            ("can_export_incidents" , "Peut exporter les incidents") ,
        ]

    def __str__(self):
        return f"Incident {self.title} - {self.incident_date.strftime('%d/%m/%Y %H:%M')}"
