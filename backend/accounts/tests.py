"""Roles y permisos.

El reparto: los **permisos** se declaran en `permissions.py` porque cada uno
existe gracias a código que lo comprueba; los **roles** son datos y se
gestionan desde pantalla.

Lo que se prueba acá es que ese reparto se sostenga de punta a punta: que el
rol de una persona termine convertido en permisos dentro de su token, y que
una vista los exija de verdad.
"""
from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

import jwt
from django.conf import settings

from accounts.models import Membership, Role, RolePermission, User
from accounts.tokens import issue_tokens
from permissions import ALL_CODES, SERVICE_PERMISSIONS


def claims_of(user, tenant=None) -> dict:
    token = issue_tokens(user, tenant)['access']
    return jwt.decode(token, settings.JWT_SIGNING_KEY, algorithms=['HS256'])


class PermissionCatalogTests(TenantTestCase):
    """El catálogo en sí. Errores acá se propagan a todo lo demás."""

    def test_codes_are_unique(self):
        codes = [code for code, _m, _d in SERVICE_PERMISSIONS]
        self.assertEqual(len(codes), len(set(codes)))

    def test_every_code_is_prefixed_with_the_service(self):
        """El IAM junta los permisos de todos los servicios en una sola lista:
        sin prefijo, dos servicios podrían chocar."""
        for code, _m, _d in SERVICE_PERMISSIONS:
            self.assertTrue(code.startswith('OUTREACH_'), f'{code} sin prefijo')

    def test_every_permission_has_a_description(self):
        """La descripción es lo que se lee en la pantalla de roles: sin ella,
        quien reparte permisos ve un código y adivina."""
        for code, _module, description in SERVICE_PERMISSIONS:
            self.assertTrue(description.strip(), f'{code} sin descripción')


class TokenPermissionTests(TenantTestCase):
    """Del rol al token."""

    def setUp(self):
        self.user = User.objects.create_user(username='ana', password='x')
        self.role = Role.objects.create(code='COORD', name='Coordinadora')
        RolePermission.objects.create(role=self.role, code='OUTREACH_PROJECT_VIEW')
        RolePermission.objects.create(role=self.role, code='OUTREACH_PROJECT_CREATE')
        Membership.objects.create(user=self.user, tenant=self.tenant, role=self.role)

    def test_the_token_carries_the_permissions_of_the_role(self):
        permisos = claims_of(self.user)['permissions']
        self.assertIn('OUTREACH_PROJECT_VIEW', permisos)
        self.assertIn('OUTREACH_PROJECT_CREATE', permisos)

    def test_it_carries_only_those(self):
        permisos = claims_of(self.user)['permissions']
        self.assertNotIn('OUTREACH_PROJECT_ARCHIVE', permisos)

    def test_the_token_names_the_active_role(self):
        rol = claims_of(self.user)['active_role']
        self.assertEqual(rol['code'], 'COORD')

    def test_someone_without_a_role_gets_no_permissions(self):
        suelto = User.objects.create_user(username='suelto', password='x')
        Membership.objects.create(user=suelto, tenant=self.tenant)

        self.assertEqual(claims_of(suelto)['permissions'], [])

    def test_changing_the_role_changes_the_next_token(self):
        """Los permisos viajan dentro del token, así que un cambio se ve al
        emitir uno nuevo — no en el que la persona ya tiene en la mano."""
        RolePermission.objects.create(role=self.role, code='OUTREACH_PROJECT_ARCHIVE')

        self.assertIn('OUTREACH_PROJECT_ARCHIVE', claims_of(self.user)['permissions'])


class ViewPermissionTests(TenantTestCase):
    """Que las vistas los exijan de verdad."""

    def setUp(self):
        self.client = TenantClient(self.tenant)
        self.url = reverse('v1:ent-project-list')

        self.lector = self._with(['OUTREACH_PROJECT_VIEW'], 'lectora')
        self.creador = self._with(
            ['OUTREACH_PROJECT_VIEW', 'OUTREACH_PROJECT_CREATE'], 'creadora',
        )
        self.sin_rol = User.objects.create_user(username='nadie', password='x')
        Membership.objects.create(user=self.sin_rol, tenant=self.tenant)

    def _with(self, permisos, username):
        user = User.objects.create_user(username=username, password='x')
        role = Role.objects.create(code=username.upper(), name=username)
        for code in permisos:
            RolePermission.objects.create(role=role, code=code)
        Membership.objects.create(user=user, tenant=self.tenant, role=role)
        return user

    def _headers(self, user):
        return {'HTTP_AUTHORIZATION': f"Bearer {issue_tokens(user)['access']}"}

    def test_without_the_view_permission_the_listing_is_forbidden(self):
        response = self.client.get(self.url, **self._headers(self.sin_rol))
        self.assertEqual(response.status_code, 403)

    def test_with_it_the_listing_works(self):
        response = self.client.get(self.url, **self._headers(self.lector))
        self.assertEqual(response.status_code, 200)

    def test_seeing_does_not_allow_creating(self):
        """El caso que justifica separar los permisos por método."""
        response = self.client.post(
            self.url, {'title': 'Un proyecto'},
            content_type='application/json', **self._headers(self.lector),
        )
        self.assertEqual(response.status_code, 403)

    def test_with_the_create_permission_it_works(self):
        response = self.client.post(
            self.url, {'title': 'Un proyecto'},
            content_type='application/json', **self._headers(self.creador),
        )
        self.assertEqual(response.status_code, 201)

    def test_a_superuser_passes_without_a_role(self):
        """Es la salida de emergencia: sin ella, un reparto de permisos mal
        hecho podría dejar a todos fuera del sistema."""
        jefa = User.objects.create_superuser(username='jefa', password='x')
        Membership.objects.create(user=jefa, tenant=self.tenant)

        response = self.client.get(self.url, **self._headers(jefa))
        self.assertEqual(response.status_code, 200)


class SeededRoleTests(TenantTestCase):
    """Los roles que siembra `seed_roles`."""

    def setUp(self):
        from django.core.management import call_command
        from io import StringIO
        call_command('seed_roles', stdout=StringIO())

    def test_the_sixteen_process_roles_are_there(self):
        self.assertEqual(Role.objects.filter(is_system=False).count(), 16)

    def test_they_are_split_between_position_and_project(self):
        """La distinción no es cosmética: un permiso de módulo no significa
        nada en un rol que se es solo dentro de un proyecto."""
        self.assertTrue(Role.objects.filter(scope=Role.Scope.INSTITUTIONAL).exists())
        self.assertTrue(Role.objects.filter(scope=Role.Scope.PROJECT).exists())

    def test_no_seeded_permission_is_outside_the_catalog(self):
        """Una errata en la siembra crearía un permiso que ninguna vista
        comprueba: existiría en la pantalla sin proteger nada."""
        for code in RolePermission.objects.values_list('code', flat=True).distinct():
            self.assertIn(code, ALL_CODES, f'"{code}" no está en el catálogo')

    def test_seeding_twice_does_not_duplicate(self):
        from django.core.management import call_command
        from io import StringIO

        antes = Role.objects.count()
        call_command('seed_roles', stdout=StringIO())

        self.assertEqual(Role.objects.count(), antes)
