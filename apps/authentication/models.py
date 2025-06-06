from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):

    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        MAGISTRATE = 'MAGISTRATE', _('Magistrat')
        GUARD = 'GUARD', _('Agent pénitentiaire')
        SOCIAL_WORKER = 'SOCIAL', _('Agent social')

    email = models.EmailField(_('adresse email'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.GUARD,
        verbose_name=_('rôle')
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('numéro de téléphone')
    )
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        verbose_name=_('photo de profil')
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        verbose_name=_('authentification à deux facteurs')
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('dernière IP de connexion')
    )

    def is_magistrate(self):
        return self.role == self.Roles.MAGISTRATE

    def is_guard(self):
        return self.role == self.Roles.GUARD

    def is_social_worker(self):
        return self.role == self.Roles.SOCIAL_WORKER

    def is_admin(self):
        return self.role == self.Roles.ADMIN

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
