"""Identidad visual editable.

Leer el branding es público —la pantalla de acceso necesita los colores antes
de que nadie inicie sesión— pero **escribirlo exige administrador**, porque
cambia lo que ve toda la institución. Mismo criterio que el IAM de InnoTech.

Los colores se guardan como texto y terminan dentro de un `style` del
navegador, así que el formato se valida en el servidor y no solo en la
pantalla.
"""
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
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

    def test_it_returns_the_identity_fields(self):
        data = self.client.get(reverse('v1:branding')).json()['data']
        for field in ('name', 'subtitle', 'logo_url'):
            self.assertIn(field, data)

    def test_without_a_logo_the_url_is_null_and_not_an_error(self):
        """La cabecera decide entre el logo y la inicial mirando este campo."""
        self.assertIsNone(self.client.get(reverse('v1:branding')).json()['data']['logo_url'])


class BrandingLogoTests(TenantTestCase):
    """Subir y quitar el logotipo.

    Va por su propia ruta porque un archivo viaja como `multipart` y el resto
    de la identidad como JSON.

    Los archivos van a un directorio temporal y **no** al de la aplicación: la
    suite corre como root y dejaría carpetas que el servidor, que corre con
    otro usuario, después no puede escribir.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._media)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        shutil.rmtree(cls._media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.client = TenantClient(self.tenant)
        self.url = reverse('v1:branding-logo')
        self.admin = User.objects.create_superuser(username='jefa', password='x')
        self.plain = User.objects.create_user(username='comun', password='x')
        self.tenant.refresh_from_db()

    def tearDown(self):
        self.tenant.refresh_from_db()
        if self.tenant.logo:
            self.tenant.logo.delete(save=True)

    def _headers(self, user):
        return {'HTTP_AUTHORIZATION': f"Bearer {issue_tokens(user)['access']}"}

    def _png(self, name='logo.png', size=64):
        # Un PNG mínimo de verdad, para que la validación de extensión y peso
        # trabaje sobre un archivo real.
        return SimpleUploadedFile(name, b'\x89PNG\r\n\x1a\n' + b'0' * size, 'image/png')

    def test_an_admin_can_upload_it(self):
        response = self.client.post(
            self.url, {'logo': self._png()}, **self._headers(self.admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json()['data']['logo_url'])

    def test_a_regular_user_cannot(self):
        response = self.client.post(
            self.url, {'logo': self._png()}, **self._headers(self.plain),
        )
        self.assertEqual(response.status_code, 403)

    def test_a_forbidden_extension_is_rejected(self):
        """Lo que se sube termina servido a un navegador: no puede ser
        cualquier cosa."""
        malo = SimpleUploadedFile('script.html', b'<script>alert(1)</script>', 'text/html')
        response = self.client.post(self.url, {'logo': malo}, **self._headers(self.admin))

        self.assertEqual(response.status_code, 400)
        self.assertIn('logo', response.json()['errors'])

    def test_a_file_that_is_too_heavy_is_rejected(self):
        """El tope evita que alguien suba la foto de un evento por
        equivocación y la cabecera tarde en cargar."""
        pesado = SimpleUploadedFile('grande.png', b'\x89PNG' + b'0' * (3 * 1024 * 1024), 'image/png')
        response = self.client.post(self.url, {'logo': pesado}, **self._headers(self.admin))

        self.assertEqual(response.status_code, 400)

    def test_uploading_without_a_file_says_so(self):
        response = self.client.post(self.url, {}, **self._headers(self.admin))
        self.assertEqual(response.status_code, 400)

    def test_it_can_be_removed(self):
        self.client.post(self.url, {'logo': self._png()}, **self._headers(self.admin))

        response = self.client.delete(self.url, **self._headers(self.admin))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()['data']['logo_url'])

    def test_every_endpoint_returns_an_absolute_url(self):
        """El navegador que la consume está en otro puerto: una ruta relativa
        la buscaría en su propio servidor y saldría la imagen rota.

        Se comprueban las tres respuestas que traen el logo, porque el fallo
        real fue que una de ellas la devolvía relativa.
        """
        subida = self.client.post(
            self.url, {'logo': self._png()}, **self._headers(self.admin),
        ).json()['data']['logo_url']

        publica = self.client.get(reverse('v1:branding')).json()['data']['logo_url']

        admin = self.client.get(
            reverse('v1:branding-settings'), **self._headers(self.admin),
        ).json()['data']['logo_url']

        for donde, url in (('al subir', subida), ('branding público', publica),
                           ('branding editable', admin)):
            self.assertTrue(
                url and url.startswith('http'),
                f'La URL de {donde} no es absoluta: {url!r}',
            )

    def test_removing_when_there_is_none_does_not_fail(self):
        self.assertEqual(
            self.client.delete(self.url, **self._headers(self.admin)).status_code, 200,
        )


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

    # ── Nombre y subtítulo ───────────────────────────────────────────

    def test_the_name_can_be_corrected(self):
        """Sin IAM nadie más puede arreglarlo: `create_tenant_local` solo pone
        el nombre al crear, así que un error quedaría congelado."""
        response = self._patch({'name': 'Instituto Corregido'}, user=self.admin)
        self.assertEqual(response.status_code, 200)

        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.name, 'Instituto Corregido')

    def test_an_empty_name_is_rejected(self):
        """La cabecera se queda sin nada que mostrar y la inicial del logo
        tampoco se puede calcular."""
        response = self._patch({'name': '   '}, user=self.admin)
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.json()['errors'])

    def test_the_subtitle_can_be_changed(self):
        self._patch({'subtitle': 'Vinculación y Emprendimiento'}, user=self.admin)

        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.subtitle, 'Vinculación y Emprendimiento')

    def test_the_subtitle_can_be_emptied(self):
        """A diferencia del nombre, quedarse sin subtítulo es una opción
        válida: la cabecera simplemente no lo muestra."""
        response = self._patch({'subtitle': ''}, user=self.admin)
        self.assertEqual(response.status_code, 200)

        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.subtitle, '')

    def test_a_name_that_is_too_long_is_rejected(self):
        self.assertEqual(
            self._patch({'name': 'x' * 300}, user=self.admin).status_code, 400,
        )
