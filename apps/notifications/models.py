from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone  # Ajout de l'import manquant

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('alert', 'Alerte'),
        ('info', 'Information'),
        ('warning', 'Avertissement'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='info',
        verbose_name="Type de notifications"
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_notifications',
        verbose_name="Destinataire"
    )
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    def __str__(self):
        return f"{self.title} - {self.recipient}"

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']