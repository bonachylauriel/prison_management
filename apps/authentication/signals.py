from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Vous pouvez ajouter ici une logique supplémentaire pour la création du profil
        pass

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Vous pouvez ajouter ici une logique supplémentaire pour la sauvegarde du profil
    pass