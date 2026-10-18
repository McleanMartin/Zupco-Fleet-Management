"""
Role definitions for ZUPCO Fleet Management.

Roles are implemented as Django auth Groups. Each role maps to a fixed set of
model permissions; a user's role is the group they belong to. Run
`python manage.py setup_roles` (or `migrate`) to create/sync the groups.
"""
from django.contrib.auth.models import Group, Permission

ADMINISTRATOR = 'Administrator'
FLEET_MANAGER = 'Fleet Manager'
DISPATCHER = 'Dispatcher'
DRIVER = 'Driver'
VIEWER = 'Viewer'

FLEET_MODELS = ['vehicle', 'location', 'route', 'routepoint', 'trip', 'fuelrecord', 'driver']


def _perms(actions, models, app_label='fleet'):
    return [f'{app_label}.{action}_{model}' for model in models for action in actions]


ALL_ACTIONS = ['view', 'add', 'change', 'delete']

ROLE_PERMISSIONS = {
    ADMINISTRATOR: (
        _perms(ALL_ACTIONS, FLEET_MODELS)
        + _perms(ALL_ACTIONS, ['user', 'group'], app_label='auth')
    ),
    FLEET_MANAGER: (
        _perms(ALL_ACTIONS, FLEET_MODELS)
        + ['auth.view_user']
    ),
    DISPATCHER: (
        _perms(['view'], FLEET_MODELS)
        + _perms(['add', 'change'], ['trip'])
    ),
    DRIVER: (
        _perms(['view'], ['vehicle', 'location', 'route', 'routepoint', 'trip'])
        + ['fleet.change_trip', 'fleet.view_fuelrecord', 'fleet.add_fuelrecord']
    ),
    VIEWER: _perms(['view'], FLEET_MODELS),
}

ROLE_DESCRIPTIONS = {
    ADMINISTRATOR: 'Full access, including user and role management.',
    FLEET_MANAGER: 'Manages vehicles, drivers, routes, trips and fuel records.',
    DISPATCHER: 'Schedules and updates trips; read-only access to everything else.',
    DRIVER: 'Views assigned routes and trips, updates trip status and logs fuel.',
    VIEWER: 'Read-only access to fleet data.',
}

ROLE_CHOICES = [(name, name) for name in ROLE_PERMISSIONS]


def _get_permission(perm):
    app_label, codename = perm.split('.', 1)
    return Permission.objects.get(content_type__app_label=app_label, codename=codename)


def sync_roles():
    """Create the role groups and set their permissions to match ROLE_PERMISSIONS."""
    for role, perms in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=role)
        group.permissions.set([_get_permission(p) for p in perms])


def get_role(user):
    """Return the user's role name, or None if they have no role."""
    group = user.groups.filter(name__in=ROLE_PERMISSIONS).first()
    return group.name if group else None


def assign_role(user, role):
    """Make `role` the user's only role (other non-role groups are kept)."""
    user.groups.remove(*Group.objects.filter(name__in=ROLE_PERMISSIONS))
    if role:
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
