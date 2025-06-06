from django.db import models
from django.utils import timezone
from django.db.models import Count , Avg
from datetime import timedelta
from django.core.exceptions import ValidationError


class Prison(models.Model):
    PROVINCES = [
        ('EST' , 'Estuaire') ,
        ('HO' , 'Haut-Ogooué') ,
        ('MO' , 'Moyen-Ogooué') ,
        ('NGO' , 'Ngounié') ,
        ('NY' , 'Nyanga') ,
        ('OI' , 'Ogooué-Ivindo') ,
        ('OL' , 'Ogooué-Lolo') ,
        ('OM' , 'Ogooué-Maritime') ,
        ('WN' , 'Woleu-Ntem') ,
    ]

    name = models.CharField(max_length=100 , verbose_name="Nom de la prison")
    province = models.CharField(
        max_length=3 ,
        choices=PROVINCES ,
        verbose_name="Province"
    )
    capacity = models.IntegerField(verbose_name="Capacité")
    current_population = models.IntegerField(
        default=0 ,
        verbose_name="Population actuelle"
    )
    created_at = models.DateTimeField(
        default=timezone.now ,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True ,
        verbose_name="Date de mise à jour"
    )
    connected_prisons = models.ManyToManyField(
        'self' ,
        through='PrisonConnection' ,
        through_fields=('prison_from' , 'prison_to') ,
        symmetrical=False ,
        related_name='connected_to' ,
        verbose_name="Prisons connectées"
    )

    def __str__(self):
        return f"Prison de {self.get_province_display()}"

    def get_occupation_rate(self):
        """Retourne le taux d'occupation en pourcentage"""
        if self.capacity > 0:
            return (self.current_population / self.capacity) * 100
        return 0

    def is_overcrowded(self):
        """Indique si la prison est en surpopulation"""
        return self.current_population > self.capacity

    def get_occupation_status(self):
        """Retourne le statut d'occupation avec une couleur associée"""
        rate = self.get_occupation_rate()
        if rate >= 100:
            return ('Surpeuplée' , 'danger')
        elif rate >= 90:
            return ('Presque pleine' , 'warning')
        elif rate >= 70:
            return ('Bien occupée' , 'info')
        else:
            return ('Normale' , 'success')

    def get_statistics(self):
        """Retourne les statistiques détaillées de la prison"""
        now = timezone.now()
        inmates = self.inmate_set.all()

        return {
            'total_inmates': self.current_population ,
            'occupation_rate': self.get_occupation_rate() ,
            'male_inmates': inmates.filter(gender='M').count() ,
            'female_inmates': inmates.filter(gender='F').count() ,
            'recidivists': inmates.filter(is_recidivist=True).count() ,
            'pending_releases': inmates.filter(
                release_date__isnull=False ,
                release_date__gt=now
            ).count() ,
            'recent_admissions': inmates.filter(
                admission_date__gte=now - timedelta(days=30)
            ).count() ,
        }

    def get_monthly_population_data(self):
        """Retourne l'évolution de la population sur les 12 derniers mois"""
        now = timezone.now()
        months_data = []

        for i in range(12 , -1 , -1):
            date = now - timedelta(days=30 * i)
            inmates_count = self.inmate_set.filter(
                admission_date__lte=date
            ).exclude(
                release_date__isnull=False ,
                release_date__lt=date
            ).count()

            months_data.append({
                'date': date.strftime('%Y-%m') ,
                'count': inmates_count
            })

        return months_data

    def update_current_population(self):
        """Met à jour la population actuelle"""
        now = timezone.now()
        current_count = self.inmate_set.filter(
            admission_date__lte=now
        ).exclude(
            release_date__isnull=False ,
            release_date__lt=now
        ).count()

        self.current_population = current_count
        self.save()

    def can_receive_inmates(self , number_of_inmates=1):
        """Vérifie si la prison peut recevoir un nombre donné de détenus"""
        return (self.current_population + number_of_inmates) <= self.capacity

    def get_available_connections(self):
        """Retourne les connexions actives avec d'autres prisons"""
        return self.connections_from.filter(is_active=True)

    def can_transfer_to(self , destination_prison , number_of_inmates=1):
        """Vérifie si un transfert est possible vers une prison donnée"""
        try:
            connection = PrisonConnection.objects.get(
                prison_from=self ,
                prison_to=destination_prison ,
                is_active=True
            )
            return (connection.max_transfer_capacity >= number_of_inmates and
                    destination_prison.can_receive_inmates(number_of_inmates))
        except PrisonConnection.DoesNotExist:
            return False

    def check_inmate_duplicates(self , inmate_number):
        """Vérifie les doublons dans les prisons connectées"""
        for connection in self.get_available_connections():
            if connection.prison_to.inmate_set.filter(
                    inmate_number=inmate_number
            ).exists():
                return True , connection.prison_to
        return False , None

    class Meta:
        verbose_name = "Prison"
        verbose_name_plural = "Prisons"


class PrisonConnection(models.Model):
    prison_from = models.ForeignKey(
        Prison ,
        on_delete=models.CASCADE ,
        related_name='connections_from' ,
        verbose_name="Prison de départ"
    )
    prison_to = models.ForeignKey(
        Prison ,
        on_delete=models.CASCADE ,
        related_name='connections_to' ,
        verbose_name="Prison d'arrivée"
    )
    established_date = models.DateField(
        auto_now_add=True ,
        verbose_name="Date d'établissement"
    )
    is_active = models.BooleanField(
        default=True ,
        verbose_name="Active"
    )
    max_transfer_capacity = models.PositiveIntegerField(
        verbose_name="Capacité maximale de transfert" ,
        help_text="Nombre maximum de détenus pouvant être transférés simultanément"
    )
    distance_km = models.DecimalField(
        verbose_name="Distance (km)" ,
        max_digits=6 ,
        decimal_places=2
    )
    notes = models.TextField(
        blank=True ,
        null=True ,
        verbose_name="Notes"
    )

    class Meta:
        unique_together = ('prison_from' , 'prison_to')
        verbose_name = "Connexion entre prisons"
        verbose_name_plural = "Connexions entre prisons"

    def clean(self):
        if self.prison_from == self.prison_to:
            raise ValidationError("Une prison ne peut pas être connectée à elle-même")

    def __str__(self):
        return f"Connexion {self.prison_from.name} → {self.prison_to.name}"


class TransferLog(models.Model):
    connection = models.ForeignKey(
        PrisonConnection ,
        on_delete=models.PROTECT ,
        verbose_name="Connexion"
    )
    transfer_date = models.DateTimeField(
        auto_now_add=True ,
        verbose_name="Date de transfert"
    )
    number_of_inmates = models.PositiveIntegerField(
        verbose_name="Nombre de détenus"
    )
    success = models.BooleanField(
        default=True ,
        verbose_name="Succès"
    )
    notes = models.TextField(
        blank=True ,
        verbose_name="Notes"
    )

    class Meta:
        verbose_name = "Journal de transfert"
        verbose_name_plural = "Journal des transferts"

    def __str__(self):
        return f"Transfert {self.connection} le {self.transfer_date}"