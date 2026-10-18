"""
Tests for roles, user management and driver management.
"""
from datetime import date

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from apps.core.roles import (
    ADMINISTRATOR, DISPATCHER, DRIVER, FLEET_MANAGER, ROLE_PERMISSIONS, VIEWER, assign_role, get_role,
)
from apps.fleet.models import Driver, Vehicle

PASSWORD = 'Zupc0-Fleet-Pass!'


def make_user(username, role=None, **kwargs):
    user = User.objects.create_user(username=username, password=PASSWORD, **kwargs)
    assign_role(user, role)
    return User.objects.get(pk=user.pk)  # fresh instance, no cached perms


class RoleSetupTests(TestCase):
    """Roles are created by the post_migrate hook when the test DB is built."""

    def test_all_roles_exist_with_permissions(self):
        for role, perms in ROLE_PERMISSIONS.items():
            group = Group.objects.get(name=role)
            self.assertEqual(group.permissions.count(), len(perms), role)

    def test_role_permissions(self):
        admin = make_user('admin', ADMINISTRATOR)
        manager = make_user('manager', FLEET_MANAGER)
        dispatcher = make_user('dispatcher', DISPATCHER)
        driver = make_user('driver', DRIVER)
        viewer = make_user('viewer', VIEWER)

        self.assertTrue(admin.has_perm('auth.add_user'))
        self.assertFalse(manager.has_perm('auth.add_user'))
        self.assertTrue(manager.has_perm('fleet.add_driver'))
        self.assertTrue(dispatcher.has_perm('fleet.add_trip'))
        self.assertFalse(dispatcher.has_perm('fleet.add_vehicle'))
        self.assertTrue(driver.has_perm('fleet.change_trip'))
        self.assertFalse(driver.has_perm('fleet.view_driver'))
        self.assertTrue(viewer.has_perm('fleet.view_vehicle'))
        self.assertFalse(viewer.has_perm('fleet.change_vehicle'))

    def test_assign_role_replaces_previous_role(self):
        user = make_user('someone', VIEWER)
        assign_role(user, DISPATCHER)
        self.assertEqual(get_role(user), DISPATCHER)
        self.assertEqual(user.groups.count(), 1)


class UserManagementTests(TestCase):

    def setUp(self):
        self.admin = make_user('admin', ADMINISTRATOR)
        self.client.force_login(self.admin)

    def test_create_user_with_role(self):
        response = self.client.post(reverse('core:user_create'), {
            'username': 'dispatch1',
            'email': 'dispatch1@example.com',
            'first_name': 'Tendai',
            'last_name': 'Moyo',
            'is_active': 'on',
            'role': DISPATCHER,
            'password': PASSWORD,
            'password_confirm': PASSWORD,
        })
        self.assertRedirects(response, reverse('core:user_list'))
        user = User.objects.get(username='dispatch1')
        self.assertEqual(get_role(user), DISPATCHER)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertFalse(user.is_superuser)

    def test_create_user_requires_matching_passwords(self):
        response = self.client.post(reverse('core:user_create'), {
            'username': 'x', 'role': VIEWER, 'password': PASSWORD, 'password_confirm': 'other',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='x').exists())

    def test_non_superuser_cannot_grant_superuser(self):
        self.client.post(reverse('core:user_create'), {
            'username': 'sneaky', 'is_active': 'on', 'is_superuser': 'on', 'role': VIEWER,
            'password': PASSWORD, 'password_confirm': PASSWORD,
        })
        self.assertFalse(User.objects.get(username='sneaky').is_superuser)

    def test_non_superuser_cannot_edit_superuser(self):
        root = User.objects.create_superuser('root', password=PASSWORD)
        response = self.client.get(reverse('core:user_edit', args=[root.pk]))
        self.assertRedirects(response, reverse('core:user_list'))

    def test_edit_user_changes_role_and_keeps_password(self):
        user = make_user('viewer', VIEWER)
        self.client.post(reverse('core:user_edit', args=[user.pk]), {
            'username': 'viewer', 'is_active': 'on', 'role': FLEET_MANAGER,
            'password': '', 'password_confirm': '',
        })
        user.refresh_from_db()
        self.assertEqual(get_role(user), FLEET_MANAGER)
        self.assertTrue(user.check_password(PASSWORD))

    def test_user_pages_forbidden_without_permission(self):
        self.client.force_login(make_user('manager', FLEET_MANAGER))
        self.assertEqual(self.client.get(reverse('core:user_create')).status_code, 403)
        self.assertEqual(self.client.get(reverse('core:role_list')).status_code, 403)
        self.assertEqual(self.client.get(reverse('core:user_list')).status_code, 200)

    def test_pages_render(self):
        user = make_user('viewer', VIEWER)
        for url in [
            reverse('core:user_list'),
            reverse('core:user_create'),
            reverse('core:user_edit', args=[user.pk]),
            reverse('core:user_delete', args=[user.pk]),
        ]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_role_list(self):
        response = self.client.get(reverse('core:role_list'))
        self.assertEqual(response.status_code, 200)
        for role in ROLE_PERMISSIONS:
            self.assertContains(response, role)


class DriverManagementTests(TestCase):

    def setUp(self):
        self.manager = make_user('manager', FLEET_MANAGER)
        self.client.force_login(self.manager)
        self.vehicle = Vehicle.objects.create(registration='ZUP-001', make='Yutong', model='ZK6', year=2022)

    def driver_data(self, **overrides):
        data = {
            'first_name': 'Farai',
            'last_name': 'Chikwanha',
            'employee_number': 'EMP001',
            'phone': '+263771234567',
            'license_number': 'LIC12345',
            'license_class': '1',
            'license_expiry': '2030-01-01',
            'assigned_vehicle': self.vehicle.pk,
            'status': 'active',
            'username': '',
            'password': '',
            'password_confirm': '',
        }
        data.update(overrides)
        return data

    def test_create_driver_without_account(self):
        response = self.client.post(reverse('drivers:create'), self.driver_data())
        self.assertRedirects(response, reverse('drivers:list'))
        driver = Driver.objects.get(employee_number='EMP001')
        self.assertIsNone(driver.user)
        self.assertEqual(driver.assigned_vehicle, self.vehicle)

    def test_create_driver_with_account_gets_driver_role(self):
        self.client.post(reverse('drivers:create'), self.driver_data(
            username='farai', password=PASSWORD, password_confirm=PASSWORD,
        ))
        driver = Driver.objects.get(employee_number='EMP001')
        self.assertEqual(driver.user.username, 'farai')
        self.assertEqual(driver.user.first_name, 'Farai')
        self.assertEqual(get_role(driver.user), DRIVER)
        self.assertTrue(driver.user.check_password(PASSWORD))

    def test_create_driver_account_requires_password(self):
        response = self.client.post(reverse('drivers:create'), self.driver_data(username='farai'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Driver.objects.exists())
        self.assertFalse(User.objects.filter(username='farai').exists())

    def test_edit_driver_keeps_account(self):
        self.client.post(reverse('drivers:create'), self.driver_data(
            username='farai', password=PASSWORD, password_confirm=PASSWORD,
        ))
        driver = Driver.objects.get()
        self.client.post(reverse('drivers:edit', args=[driver.pk]), self.driver_data(
            username='farai', status='inactive',
        ))
        driver.refresh_from_db()
        self.assertEqual(driver.status, 'inactive')
        self.assertFalse(driver.user.is_active)
        self.assertTrue(driver.user.check_password(PASSWORD))

    def test_delete_driver_deactivates_account(self):
        self.client.post(reverse('drivers:create'), self.driver_data(
            username='farai', password=PASSWORD, password_confirm=PASSWORD,
        ))
        driver = Driver.objects.get()
        self.client.post(reverse('drivers:delete', args=[driver.pk]))
        self.assertFalse(Driver.objects.exists())
        self.assertFalse(User.objects.get(username='farai').is_active)

    def test_pages_render(self):
        self.client.post(reverse('drivers:create'), self.driver_data(
            username='farai', password=PASSWORD, password_confirm=PASSWORD,
        ))
        driver = Driver.objects.get()
        for url in [
            reverse('drivers:list'),
            reverse('drivers:create'),
            reverse('drivers:edit', args=[driver.pk]),
            reverse('drivers:delete', args=[driver.pk]),
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)
        self.assertContains(self.client.get(reverse('drivers:list')), 'Farai Chikwanha')

    def test_license_expired(self):
        driver = Driver(license_expiry=date(2000, 1, 1))
        self.assertTrue(driver.license_expired)

    def test_driver_role_cannot_manage_drivers(self):
        self.client.force_login(make_user('driver', DRIVER))
        self.assertEqual(self.client.get(reverse('drivers:list')).status_code, 403)
        self.assertEqual(self.client.get(reverse('drivers:create')).status_code, 403)


class FeaturePermissionTests(TestCase):
    """Existing feature views are gated by the role's permissions."""

    def test_viewer_can_view_but_not_edit_vehicles(self):
        self.client.force_login(make_user('viewer', VIEWER))
        self.assertEqual(self.client.get(reverse('vehicles:list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('vehicles:create')).status_code, 403)

    def test_dispatcher_can_create_trips_but_not_routes(self):
        self.client.force_login(make_user('dispatcher', DISPATCHER))
        self.assertEqual(self.client.get(reverse('trips:create')).status_code, 200)
        self.assertEqual(self.client.get(reverse('routes:create')).status_code, 403)
