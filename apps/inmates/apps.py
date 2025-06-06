from django.apps import AppConfig


class InmatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inmates'
    verbose_name = 'Gestion des Détenus'

    def ready(self):
        import apps.inmates.signals

