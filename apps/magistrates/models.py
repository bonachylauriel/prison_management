from django.db import models
from django.utils import timezone

class Magistrate(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Prénom",null=True,
        blank=True)
    last_name = models.CharField(max_length=100, verbose_name="Nom",null=True,
        blank=True)
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=20, verbose_name="Téléphone",null=True,
        blank=True)
    court_name = models.CharField(
        max_length=200,
        verbose_name="Nom du tribunal",
        default="Tribunal de Grande Instance"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de mise à jour",
        auto_now=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Magistrat"
        verbose_name_plural = "Magistrats"