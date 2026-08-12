"""La configuración del módulo.

Leerla es para cualquiera con sesión; **guardarla exige administrador**, porque
un cambio acá le cambia el comportamiento del módulo a toda la institución.
Mismo criterio que el branding.

Lo que se guarda termina componiendo el código de los proyectos, así que el
formato se valida en el servidor y no solo en la pantalla.
"""
from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from accounts.models import User
from accounts.models import Membership, Role, RolePermission
from accounts.tokens import issue_tokens
from entrepreneurship.models import Configuration


class ConfigurationTests(TenantTestCase):

    def setUp(self):
        self.client = TenantClient(self.tenant)
        self.url = reverse('v1:ent-configuration')

        # Superusuario: pasa cualquier permiso sin necesitar rol.
        self.admin = User.objects.create_superuser(username='jefa', password='x')

        # Con permiso para mirar, pero no para cambiar: es el caso que separa
        # las dos reglas de esta vista.
        self.lector = self._user_with('mirona', ['OUTREACH_SETTINGS_VIEW'])

        # Sin rol: entra al sistema pero no puede nada.
        self.plain = User.objects.create_user(username='comun', password='x')
        Membership.objects.create(user=self.plain, tenant=self.tenant)

    def _user_with(self, username, permisos):
        """Un usuario con un rol que trae exactamente esos permisos."""
        user = User.objects.create_user(username=username, password='x')
        role = Role.objects.create(code=username.upper(), name=username)
        for code in permisos:
            RolePermission.objects.create(role=role, code=code)
        Membership.objects.create(user=user, tenant=self.tenant, role=role)
        return user

    def _headers(self, user=None):
        if not user:
            return {}
        return {'HTTP_AUTHORIZATION': f"Bearer {issue_tokens(user)['access']}"}

    def _get(self, user=None):
        return self.client.get(self.url, **self._headers(user))

    def _patch(self, payload, user=None):
        return self.client.patch(
            self.url, payload, content_type='application/json', **self._headers(user),
        )

    # ── Existencia ───────────────────────────────────────────────────

    def test_it_is_created_on_first_read(self):
        """Una institución nueva no tiene fila: se crea sola con los valores
        por defecto en vez de responder 404."""
        self.assertEqual(Configuration.objects.count(), 0)

        self.assertEqual(self._get(self.lector).status_code, 200)
        self.assertEqual(Configuration.objects.count(), 1)

    def test_reading_twice_does_not_duplicate_it(self):
        self._get(self.lector)
        self._get(self.lector)
        self.assertEqual(Configuration.objects.count(), 1)

    # ── Permisos ─────────────────────────────────────────────────────

    def test_someone_with_the_view_permission_can_read_it(self):
        self.assertEqual(self._get(self.lector).status_code, 200)

    def test_someone_without_any_role_cannot_read_it(self):
        """Entrar al sistema no alcanza: hay que tener el permiso."""
        self.assertEqual(self._get(self.plain).status_code, 403)

    def test_reading_does_not_allow_changing(self):
        """El permiso de mirar y el de cambiar son distintos a propósito."""
        self.assertEqual(
            self._patch({'project_code_prefix': 'XX'}, user=self.lector).status_code,
            403,
        )

    def test_without_a_session_it_cannot_be_read(self):
        self.assertIn(self._get().status_code, (401, 403))

    def test_a_regular_user_cannot_change_it(self):
        response = self._patch({'project_code_prefix': 'XX'}, user=self.plain)
        self.assertEqual(response.status_code, 403)

    def test_an_admin_can_change_it(self):
        response = self._patch({'project_code_prefix': 'EMP'}, user=self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Configuration.load().project_code_prefix, 'EMP')

    # ── Validación ───────────────────────────────────────────────────

    def test_a_lowercase_prefix_is_rejected(self):
        response = self._patch({'project_code_prefix': 'pe'}, user=self.admin)
        self.assertEqual(response.status_code, 400)
        self.assertIn('project_code_prefix', response.json()['errors'])

    def test_a_prefix_with_spaces_is_rejected(self):
        self.assertEqual(
            self._patch({'project_code_prefix': 'P E'}, user=self.admin).status_code, 400,
        )

    def test_too_many_digits_are_rejected(self):
        """El tope evita un código de cincuenta ceros que nadie puede leer."""
        self.assertEqual(
            self._patch({'project_code_digits': 99}, user=self.admin).status_code, 400,
        )

    def test_zero_digits_are_rejected(self):
        self.assertEqual(
            self._patch({'project_code_digits': 0}, user=self.admin).status_code, 400,
        )

    # ── Ejemplo de código ────────────────────────────────────────────

    def test_it_returns_an_example_of_the_next_code(self):
        """La pantalla necesita mostrar el efecto del cambio, y la regla de
        formato vive en el backend: se manda armada."""
        data = self._get(self.lector).json()['data']
        self.assertIn('code_example', data)
        self.assertTrue(data['code_example'].startswith('PE-'))

    def test_the_example_follows_what_was_saved(self):
        self._patch(
            {'project_code_prefix': 'EMP', 'project_code_include_year': False,
             'project_code_digits': 4},
            user=self.admin,
        )
        self.assertEqual(self._get(self.lector).json()['data']['code_example'], 'EMP-0001')
