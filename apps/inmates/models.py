from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from apps.prisons.models import Prison

class Inmate(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    registration_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro d'écrou")
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    date_of_birth = models.DateField(verbose_name="Date de naissance")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Genre")

    # Nouveaux champs
    birth_date = models.DateField(verbose_name="Date de naissance", default=timezone.now)
    nationality = models.CharField(max_length=100 , verbose_name="Nationalité",  default="Français")


    photo = models.ImageField(
        upload_to='inmates_photos/%Y/%m/',
        verbose_name="Photo",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        help_text="Format accepté : JPG, JPEG, PNG",
        null=True,
        blank=True
    )
    current_prison = models.ForeignKey(Prison, on_delete=models.PROTECT, verbose_name="Prison actuelle")
    admission_date = models.DateTimeField(default=timezone.now, verbose_name="Date d'admission")
    release_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de libération")
    health_status = models.TextField(verbose_name="État de santé")
    is_recidivist = models.BooleanField(default=False, verbose_name="Récidiviste")
    crime_description = models.TextField(verbose_name="Description du crime")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    @property
    def current_detention(self):
        return self.detention_set.filter(end_date__isnull=True).first()

    @property
    def is_active(self):
        return self.current_detention is not None

    def get_criminal_record(self):
        return self.detention_set.all().order_by('-start_date')

    class Meta:
        ordering = ['-admission_date']
        verbose_name = "Détenu"
        verbose_name_plural = "Détenus"

    def __str__(self):
        return f"{self.registration_number} - {self.first_name} {self.last_name}"

class Detention(models.Model):
    RELEASE_REASONS = [
        ('FINE_PEINE' , 'Fin de peine') ,
        ('LIBERATION_CONDITIONNELLE' , 'Libération conditionnelle') ,
        ('GRACE_PRESIDENTIELLE' , 'Grâce présidentielle') ,
        ('ACQUITTEMENT' , 'Acquittement') ,
        ('AUTRE' , 'Autre')
    ]

    inmate = models.ForeignKey(Inmate, on_delete=models.CASCADE, verbose_name="Détenu")
    warrant_pdf = models.FileField(
        upload_to='detention_warrants/',
        verbose_name="Mandat de détention",
        validators=[FileExtensionValidator(['pdf'])],
        help_text="Format accepté : PDF"
    )
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Date de début")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    release_time = models.TimeField(null=True , blank=True , verbose_name="Heure de libération")
    release_reason = models.CharField(
        max_length=50 ,
        choices=RELEASE_REASONS ,
        null=True ,
        blank=True ,
        verbose_name="Motif de libération"
    )
    special_conditions = models.TextField(
        null=True ,
        blank=True ,
        verbose_name="Conditions spéciales"
    )

    magistrate = models.ForeignKey(
        'magistrates.Magistrate',
        on_delete=models.PROTECT,
        verbose_name="Magistrat"
    )
    release_magistrate = models.ForeignKey(
        'magistrates.Magistrate' ,
        on_delete=models.PROTECT ,
        related_name='releases' ,
        null=True ,
        blank=True ,
        verbose_name="Magistrat de libération"
    )

    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    # Ajout des méthodes pour les documents
    def generate_release_certificate(self):
        if not self.end_date:
            raise ValueError("Impossible de générer un certificat de libération sans date de fin")
        # Logique de génération du certificat
        return True

    def generate_criminal_record(self):
        # Logique de génération du casier judiciaire
        return True

    class Meta:
        verbose_name = "Détention"
        verbose_name_plural = "Détentions"
        ordering = ['-start_date']

    def __str__(self):
        return f"Détention de {self.inmate} - {self.start_date}"

class Visit(models.Model):
    RELATION_CHOICES = [
        ('FAMILLE', 'Famille'),
        ('CONJOINT', 'Conjoint(e)'),
        ('AMI', 'Ami(e)'),
        ('AVOCAT', 'Avocat'),
        ('AUTRE', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('PLANIFIE', 'Planifiée'),
        ('CONFIRME', 'Confirmée'),
        ('TERMINE', 'Terminée'),
        ('ANNULE', 'Annulée'),
    ]

    inmate = models.ForeignKey('Inmate', on_delete=models.CASCADE, related_name='visits',
                              verbose_name="Détenu")
    visitor_name = models.CharField(max_length=100, verbose_name="Nom du visiteur", default="Visiteur")
    visitor_id_number = models.CharField(max_length=20, verbose_name="Numéro d'identification", default="ID-00000")
    visitor_phone = models.CharField(max_length=15, verbose_name="Téléphone", default="0000000000")
    visitor_relation = models.CharField(max_length=20, choices=RELATION_CHOICES,default='AUTRE',
                                     verbose_name="Relation avec le détenu")
    date = models.DateTimeField(verbose_name="Date et heure de la visite", default=timezone.now)
    duration = models.DurationField(verbose_name="Durée prévue", default=timezone.timedelta(hours=1))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANIFIE',
                            verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes",default="")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL,
                                 null=True, related_name='visits_created')
    approved_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='visits_approved')

    class Meta:
        ordering = ['-date']
        verbose_name = "Visite"
        verbose_name_plural = "Visites"
        permissions = [
            ("can_approve_visit", "Peut approuver les visites"),
            ("can_cancel_visit", "Peut annuler les visites"),
        ]

    def __str__(self):
        return f"Visite de {self.visitor_name} à {self.inmate} le {self.date}"

