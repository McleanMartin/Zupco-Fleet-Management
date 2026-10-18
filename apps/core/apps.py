from django.apps import AppConfig, apps
from django.db.models.signals import post_migrate


def _sync_roles(sender, **kwargs):
    from .roles import sync_roles
    sync_roles()


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        # Run after the fleet app's permissions have been created.
        post_migrate.connect(_sync_roles, sender=apps.get_app_config('fleet'))
