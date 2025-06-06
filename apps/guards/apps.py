from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_permissions(sender , **kwargs):
    from django.contrib.auth.models import Group , Permission
    from django.contrib.contenttypes.models import ContentType
    from .models import User , TeamUnit , Schedule , IncidentReport

    # Création des groupes
    guard_group , _ = Group.objects.get_or_create(name='Gardes')
    senior_group , _ = Group.objects.get_or_create(name='Gardiens Principaux')
    supervisor_group , _ = Group.objects.get_or_create(name='Superviseurs')

    # Permissions pour les modèles
    models = [User , TeamUnit , Schedule , IncidentReport]

    # Permissions de base pour les gardes
    guard_permissions = [
        'view_user' ,
        'view_teamunit' ,
        'view_schedule' ,
        'add_incidentreport' ,
        'view_incidentreport' ,
        'change_incidentreport' ,
    ]

    # Permissions supplémentaires pour les gardiens principaux
    senior_permissions = guard_permissions + [
        'add_teamunit' ,
        'change_teamunit' ,
        'add_schedule' ,
        'change_schedule' ,
    ]

    # Toutes les permissions pour les superviseurs
    supervisor_permissions = []
    for model in models:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        for perm in permissions:
            supervisor_permissions.append(perm.codename)

    # Attribution des permissions aux groupes
    for codename in guard_permissions:
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            try:
                perm = Permission.objects.get(codename=codename , content_type=content_type)
                guard_group.permissions.add(perm)
            except Permission.DoesNotExist:
                continue

    for codename in senior_permissions:
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            try:
                perm = Permission.objects.get(codename=codename , content_type=content_type)
                senior_group.permissions.add(perm)
            except Permission.DoesNotExist:
                continue

    for codename in supervisor_permissions:
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            try:
                perm = Permission.objects.get(codename=codename , content_type=content_type)
                supervisor_group.permissions.add(perm)
            except Permission.DoesNotExist:
                continue


class GuardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.guards'
    label = 'guards'

    def ready(self):
        post_migrate.connect(create_permissions , sender=self)