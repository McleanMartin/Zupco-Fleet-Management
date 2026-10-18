"""
Create or update the role groups and their permissions.
"""
from django.core.management.base import BaseCommand

from apps.core.roles import ROLE_PERMISSIONS, sync_roles


class Command(BaseCommand):
    help = 'Create/update role groups (Administrator, Fleet Manager, ...) and their permissions.'

    def handle(self, *args, **options):
        sync_roles()
        for role, perms in ROLE_PERMISSIONS.items():
            self.stdout.write(f'{role}: {len(perms)} permissions')
        self.stdout.write(self.style.SUCCESS('Roles synced.'))
