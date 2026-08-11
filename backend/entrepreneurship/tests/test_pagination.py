"""Paginación del listado de proyectos.

Antes el endpoint devolvía la tabla entera y la pantalla mostraba una
paginación de adorno. Ahora pagina de verdad, y estos tests cuidan los bordes:
una página que no existe, un `page_size` absurdo, y que `count` siga siendo el
total y no lo que trae la página.
"""
from io import StringIO

from django.core.management import call_command
from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from api.v1.entrepreneurship.views import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from entrepreneurship.models import Project


class PaginationTests(TenantTestCase):

    def setUp(self):
        call_command('seed_stages', stdout=StringIO())
        self.client = TenantClient(self.tenant)
        for i in range(25):
            Project.objects.create(title=f'Proyecto {i:02d}')

    def _get(self, **params):
        response = self.client.get(
            reverse('v1:ent-project-list'),
            params,
            HTTP_X_INTERNAL_SECRET='super_secret_token',
        )
        self.assertEqual(response.status_code, 200)
        return response.json()['data']

    def test_first_page_has_the_default_size(self):
        data = self._get()
        self.assertEqual(len(data['results']), DEFAULT_PAGE_SIZE)
        self.assertEqual(data['page'], 1)

    def test_count_is_the_total_not_the_page(self):
        """`count` alimenta el cálculo de cuántas páginas hay. Si trajera lo de
        la página, la paginación mostraría siempre una sola."""
        data = self._get()
        self.assertEqual(data['count'], 25)
        self.assertEqual(data['total_pages'], 3)

    def test_pages_do_not_repeat_projects(self):
        vistos = []
        for page in (1, 2, 3):
            vistos += [p['id'] for p in self._get(page=page)['results']]
        self.assertEqual(len(vistos), 25)
        self.assertEqual(len(set(vistos)), 25, 'Alguna página repitió proyectos.')

    def test_last_page_has_the_remainder(self):
        self.assertEqual(len(self._get(page=3)['results']), 5)

    def test_a_page_out_of_range_falls_back_instead_of_failing(self):
        """Pedir la página 99 no puede ser un error 500: `get_page` acota."""
        data = self._get(page=99)
        self.assertEqual(data['page'], 3)

    def test_a_page_that_is_not_a_number_falls_back_to_the_first(self):
        self.assertEqual(self._get(page='abc')['page'], 1)

    def test_page_size_is_capped(self):
        """Sin tope, `?page_size=` grande sería la forma de pedir la tabla
        entera y dejar la paginación de adorno."""
        data = self._get(page_size=100000)
        self.assertEqual(data['page_size'], MAX_PAGE_SIZE)

    def test_a_page_size_that_is_not_a_number_uses_the_default(self):
        self.assertEqual(self._get(page_size='muchos')['page_size'], DEFAULT_PAGE_SIZE)

    def test_filtering_narrows_the_total(self):
        """El total tiene que ser el de la consulta filtrada, no el de la
        tabla: si no, la paginación ofrecería páginas vacías."""
        # Los títulos van de "Proyecto 00" a "Proyecto 24", así que "Proyecto 1"
        # casa con los diez del 10 al 19 — el 01 no, porque lleva el cero.
        data = self._get(search='Proyecto 1')
        self.assertEqual(data['count'], 10)
        self.assertEqual(data['total_pages'], 1)
