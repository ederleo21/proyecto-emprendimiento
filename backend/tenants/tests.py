"""Identidad visual editable.

Leer el branding es público —la pantalla de acceso necesita los colores antes
de que nadie inicie sesión— pero **escribirlo exige administrador**, porque
cambia lo que ve toda la institución. Mismo criterio que el IAM de InnoTech.

Los colores se guardan como texto y terminan dentro de un `style` del
navegador, así que el formato se valida en el servidor y no solo en la
pantalla.
"""
from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from accounts.models import User
from accounts.tokens import issue_tokens


class BrandingReadTests(TenantTestCase):
    """`GET /branding/` — abierto a propósito."""

    def setUp(self):
        self.client = TenantClient(self.tenant)

    def test_anyone_can_read_the_branding(self):
        response = self.client.get(reverse('v1:branding'))
        self.assertEqual(response.status_code, 200)

    def test_it_returns_both_colors(self):
        data = self.client.get(reverse('v1:branding')).json()['data']
        self.assertIn('primary_color', data)
        self.assertIn('secondary_color', data)


class BrandingWriteTests(TenantTestCase):
    """`PATCH /branding/settings/` — solo administradores."""

    def setUp(self):
        self.client = TenantClient(self.tenant)
        self.url = reverse('v1:branding-settings')
        self.admin = User.objects.create_superuser(username='jefe', password='x')
        self.plain = User.objects.create_user(username='comun', password='x')
        # `self.tenant` lo crea `TenantTestCase` una vez para toda la clase, así
        # que sobrevive en memoria a lo que cada test escriba aunque la base sí
        # revierta. Sin esto, un test lee el valor que dejó el anterior.
        self.tenant.refresh_from_db()

    def _patch(self, payload, user=None):
        """Autentica con un JWT y no con `force_login`: este servicio no tiene
        sesiones — la identidad viaja siempre en el token."""
        headers = {}
        if user:
            token = issue_tokens(user)['access']
            headers['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return self.client.patch(
            self.url, payload, content_type='application/json', **headers,
        )

    # ── Permisos ─────────────────────────────────────────────────────

    def test_without_session_it_is_rejected(self):
        self.assertIn(self._patch({'primary_color': '#FF0000'}).status_code, (401, 403))

    def test_a_regular_user_cannot_change_it(self):
        """Cambiar los colores le cambia la pantalla a toda la institución."""
        response = self._patch({'primary_color': '#FF0000'}, user=self.plain)
        self.assertEqual(response.status_code, 403)

    def test_an_admin_can_change_it(self):
        response = self._patch({'primary_color': '#FF0000'}, user=self.admin)
        self.assertEqual(response.status_code, 200)

        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.primary_color, '#FF0000')

    # ── Validación ───────────────────────────────────────────────────

    def test_it_rejects_something_that_is_not_a_color(self):
        """El valor entra en un `style` del navegador: tiene que ser un color,
        no cualquier cadena."""
        response = self._patch({'primary_color': 'javascript:alert(1)'}, user=self.admin)
        self.assertEqual(response.status_code, 400)
        self.assertIn('primary_color', response.json()['errors'])

        self.tenant.refresh_from_db()
        self.assertNotEqual(self.tenant.primary_color, 'javascript:alert(1)')

    def test_it_rejects_a_hex_of_the_wrong_length(self):
        response = self._patch({'primary_color': '#12345'}, user=self.admin)
        self.assertEqual(response.status_code, 400)

    def test_it_accepts_the_short_form(self):
        response = self._patch({'primary_color': '#f00'}, user=self.admin)
        self.assertEqual(response.status_code, 200)

    def test_an_empty_payload_is_rejected(self):
        """Sin esto, un PATCH vacío respondería 200 sin haber hecho nada."""
        self.assertEqual(self._patch({}, user=self.admin).status_code, 400)

    def test_one_color_can_be_changed_without_touching_the_other(self):
        before = self.tenant.secondary_color
        self._patch({'primary_color': '#ABCDEF'}, user=self.admin)

        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.primary_color, '#ABCDEF')
        self.assertEqual(self.tenant.secondary_color, before)

    def test_an_invalid_color_does_not_save_the_valid_one_next_to_it(self):
        """Los dos campos van juntos: si uno falla, no se guarda ninguno."""
        before = self.tenant.primary_color
        response = self._patch(
            {'primary_color': '#00FF00', 'secondary_color': 'rojo'},
            user=self.admin,
        )
        self.assertEqual(response.status_code, 400)

        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.primary_color, before)
