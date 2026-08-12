"""Gestión de roles por la API.

Lo delicado acá no es crear ni listar: son las dos puertas que no se pueden
cerrar por dentro. Si alguien se queda sin nadie que reparta permisos, o borra
un rol que tiene gente, la única salida es entrar a la base de datos.
"""
from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from accounts.models import Membership, Role, RolePermission, User
from accounts.tokens import issue_tokens

MANAGE = 'OUTREACH_ROLE_EDIT'


class RoleApiTests(TenantTestCase):

    def setUp(self):
        self.client = TenantClient(self.tenant)
        self.list_url = reverse('v1:role-list')

        # Quien gestiona. No es superusuario a propósito: así se prueba el
        # permiso y no el atajo de emergencia.
        self.jefa = self._user_with('jefa', [MANAGE, 'OUTREACH_ROLE_VIEW'])
        self.mirona = self._user_with('mirona', ['OUTREACH_ROLE_VIEW'])

    def _user_with(self, username, permisos):
        user = User.objects.create_user(username=username, password='x')
        role = Role.objects.create(code=username.upper(), name=username)
        for code in permisos:
            RolePermission.objects.create(role=role, code=code)
        Membership.objects.create(user=user, tenant=self.tenant, role=role)
        return user

    def _headers(self, user):
        return {'HTTP_AUTHORIZATION': f"Bearer {issue_tokens(user)['access']}"}

    def _detail(self, role):
        return reverse('v1:role-detail', args=[role.pk])

    # ── Permisos de la propia pantalla ───────────────────────────────

    def test_seeing_roles_does_not_allow_creating_them(self):
        response = self.client.post(
            self.list_url, {'name': 'Inventado'},
            content_type='application/json', **self._headers(self.mirona),
        )
        self.assertEqual(response.status_code, 403)

    def test_whoever_manages_can_create(self):
        response = self.client.post(
            self.list_url, {'name': 'Revisor Externo'},
            content_type='application/json', **self._headers(self.jefa),
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Role.objects.filter(name='Revisor Externo').exists())

    def test_the_code_comes_from_the_name(self):
        response = self.client.post(
            self.list_url, {'name': 'Revisión Académica'},
            content_type='application/json', **self._headers(self.jefa),
        )
        # Sin tildes ni espacios: el código viaja en el token y en asignaciones.
        self.assertEqual(response.json()['data']['code'], 'REVISION_ACADEMICA')

    def test_two_roles_cannot_share_a_name(self):
        for _ in range(2):
            response = self.client.post(
                self.list_url, {'name': 'Repetido'},
                content_type='application/json', **self._headers(self.jefa),
            )
        self.assertEqual(response.status_code, 400)

    def test_a_new_role_can_clone_the_permissions_of_another(self):
        origen = Role.objects.create(code='ORIGEN', name='Origen')
        RolePermission.objects.create(role=origen, code='OUTREACH_PROJECT_VIEW')

        response = self.client.post(
            self.list_url,
            {'name': 'Copia', 'clone_from': str(origen.pk)},
            content_type='application/json', **self._headers(self.jefa),
        )
        self.assertIn('OUTREACH_PROJECT_VIEW', response.json()['data']['permissions'])

    # ── Cambiar permisos ─────────────────────────────────────────────

    def test_permissions_can_be_replaced(self):
        role = Role.objects.create(code='OTRO', name='Otro')
        response = self.client.patch(
            self._detail(role),
            {'permissions': ['OUTREACH_PROJECT_VIEW', 'OUTREACH_PROJECT_CREATE']},
            content_type='application/json', **self._headers(self.jefa),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(role.permissions.count(), 2)

    def test_a_permission_outside_the_catalog_is_rejected(self):
        """Guardarlo dejaría una casilla marcada que no protege nada."""
        role = Role.objects.create(code='OTRO', name='Otro')
        response = self.client.patch(
            self._detail(role), {'permissions': ['INVENTADO']},
            content_type='application/json', **self._headers(self.jefa),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(role.permissions.count(), 0)

    # ── Las dos puertas que no se pueden cerrar ──────────────────────

    def test_the_last_role_that_manages_permissions_cannot_lose_it(self):
        """Si se pierde, nadie puede volver a repartir permisos y hay que
        entrar a la base de datos a arreglarlo."""
        # La migración deja el rol Administrador con todo, así que hay que
        # dejar a JEFA como el único que sostiene el permiso.
        RolePermission.objects.filter(code=MANAGE).exclude(role__code='JEFA').delete()

        unico = Role.objects.get(code='JEFA')
        response = self.client.patch(
            self._detail(unico), {'permissions': ['OUTREACH_PROJECT_VIEW']},
            content_type='application/json', **self._headers(self.jefa),
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn(MANAGE, unico.permission_codes)

    def test_it_can_lose_it_if_another_role_also_has_it(self):
        """La protección cuida que quede alguien, no un rol en particular."""
        RolePermission.objects.filter(code=MANAGE).exclude(role__code='JEFA').delete()

        respaldo = Role.objects.create(code='RESPALDO', name='Respaldo')
        RolePermission.objects.create(role=respaldo, code=MANAGE)

        unico = Role.objects.get(code='JEFA')
        response = self.client.patch(
            self._detail(unico), {'permissions': ['OUTREACH_PROJECT_VIEW']},
            content_type='application/json', **self._headers(self.jefa),
        )
        self.assertEqual(response.status_code, 200)

    def test_a_role_with_people_cannot_be_deleted(self):
        """Borrarlo dejaría a esa gente sin rol y sin poder hacer nada, sin
        que nadie se entere."""
        conmigo = Role.objects.get(code='MIRONA')

        response = self.client.delete(
            self._detail(conmigo), **self._headers(self.jefa),
        )
        self.assertEqual(response.status_code, 409)
        self.assertTrue(Role.objects.filter(pk=conmigo.pk).exists())

    def test_a_system_role_cannot_be_deleted(self):
        delsistema = Role.objects.create(code='SISTEMA', name='Del sistema', is_system=True)

        response = self.client.delete(
            self._detail(delsistema), **self._headers(self.jefa),
        )
        self.assertEqual(response.status_code, 409)

    def test_an_unused_role_can_be_deleted(self):
        suelto = Role.objects.create(code='SUELTO', name='Suelto')

        response = self.client.delete(self._detail(suelto), **self._headers(self.jefa))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Role.objects.filter(pk=suelto.pk).exists())


class PermissionCatalogApiTests(TenantTestCase):
    """El catálogo que dibuja la matriz."""

    def setUp(self):
        self.client = TenantClient(self.tenant)
        self.url = reverse('v1:role-permissions')
        self.user = User.objects.create_user(username='ana', password='x')
        role = Role.objects.create(code='VER', name='Ver')
        RolePermission.objects.create(role=role, code='OUTREACH_ROLE_VIEW')
        Membership.objects.create(user=self.user, tenant=self.tenant, role=role)

    def test_it_comes_grouped_by_module(self):
        data = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {issue_tokens(self.user)['access']}",
        ).json()['data']

        self.assertTrue(data)
        for modulo in data:
            self.assertIn('module', modulo)
            self.assertIn('permissions', modulo)

    def test_without_the_permission_it_is_forbidden(self):
        suelto = User.objects.create_user(username='suelto', password='x')
        Membership.objects.create(user=suelto, tenant=self.tenant)

        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {issue_tokens(suelto)['access']}",
        )
        self.assertEqual(response.status_code, 403)
