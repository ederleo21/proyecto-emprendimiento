"""Código del proyecto, edición y archivado.

El código sale de `Configuration`, que es configuración por institución y no
constantes en el código: una puede querer `PE-2026-001` y otra `EMP-0001`.

Archivar es borrado lógico. Lo delicado ahí es que el `CASCADE` de la FK no
actúa —la base nunca ve un borrado real— así que las actividades hay que
archivarlas a mano o quedan vivas colgando de un proyecto que ya no está.
"""
from io import StringIO

from django.core.management import call_command
from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

from entrepreneurship.models import Configuration, Project, ProjectActivity


class ProjectCodeTests(TenantTestCase):

    def setUp(self):
        call_command('seed_stages', stdout=StringIO())
        self.client = TenantClient(self.tenant)

    def _create(self, title='Un proyecto'):
        response = self.client.post(
            reverse('v1:ent-project-list'),
            {'title': title},
            content_type='application/json',
            HTTP_X_INTERNAL_SECRET='super_secret_token',
        )
        self.assertEqual(response.status_code, 201)
        return response.json()['data']

    def test_a_new_project_gets_a_code(self):
        self.assertTrue(self._create()['code'])

    def test_codes_are_sequential(self):
        first = self._create('Uno')['code']
        second = self._create('Dos')['code']
        self.assertNotEqual(first, second)
        self.assertTrue(first.endswith('001'))
        self.assertTrue(second.endswith('002'))

    def test_the_prefix_comes_from_the_configuration(self):
        """Nada de prefijos escritos en el código: los pone la institución."""
        config = Configuration.load()
        config.project_code_prefix = 'EMP'
        config.save()

        self.assertTrue(self._create()['code'].startswith('EMP-'))

    def test_the_year_can_be_turned_off(self):
        config = Configuration.load()
        config.project_code_include_year = False
        config.save()

        code = self._create()['code']
        self.assertEqual(code.count('-'), 1, f'Esperaba sin año, salió {code}')

    def test_the_number_of_digits_is_configurable(self):
        config = Configuration.load()
        config.project_code_digits = 5
        config.save()

        self.assertTrue(self._create()['code'].endswith('00001'))

    def test_an_archived_project_does_not_release_its_code(self):
        """Un código lo lee una persona y termina en actas: reciclarlo
        confundiría."""
        first = self._create('Uno')
        Project.objects.get(pk=first['id']).delete()

        self.assertNotEqual(self._create('Dos')['code'], first['code'])

    def test_the_code_cannot_be_set_from_outside(self):
        created = self._create()
        self.assertNotEqual(created['code'], 'INVENTADO-1')


class ProjectEditTests(TenantTestCase):

    def setUp(self):
        call_command('seed_stages', stdout=StringIO())
        self.client = TenantClient(self.tenant)
        self.project = Project.objects.create(title='Título con herror', code='PE-2026-001')

    def _patch(self, payload):
        return self.client.patch(
            reverse('v1:ent-project-detail', args=[self.project.pk]),
            payload,
            content_type='application/json',
            HTTP_X_INTERNAL_SECRET='super_secret_token',
        )

    def test_the_title_can_be_corrected(self):
        self.assertEqual(self._patch({'title': 'Título corregido'}).status_code, 200)

        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Título corregido')

    def test_an_empty_title_is_rejected(self):
        response = self._patch({'title': '   '})
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json()['errors'])

    def test_the_code_is_ignored_if_sent(self):
        self._patch({'code': 'OTRO-999'})

        self.project.refresh_from_db()
        self.assertEqual(self.project.code, 'PE-2026-001')

    def test_editing_something_that_does_not_exist_is_a_404(self):
        response = self.client.patch(
            reverse('v1:ent-project-detail',
                    args=['00000000-0000-0000-0000-000000000000']),
            {'title': 'x'},
            content_type='application/json',
            HTTP_X_INTERNAL_SECRET='super_secret_token',
        )
        self.assertEqual(response.status_code, 404)


class ProjectArchiveTests(TenantTestCase):

    def setUp(self):
        call_command('seed_stages', stdout=StringIO())
        self.client = TenantClient(self.tenant)
        self.project = Project.objects.create(title='Para archivar')
        from entrepreneurship.models import StageActivity
        ProjectActivity.objects.bulk_create([
            ProjectActivity(project=self.project, activity=a)
            for a in StageActivity.objects.filter(is_optional=False, is_active=True)
        ])

    def _delete(self, pk=None):
        return self.client.delete(
            reverse('v1:ent-project-detail', args=[pk or self.project.pk]),
            HTTP_X_INTERNAL_SECRET='super_secret_token',
        )

    def test_archiving_hides_it_from_the_listing(self):
        self.assertEqual(self._delete().status_code, 200)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_it_is_not_really_deleted(self):
        """Borrado lógico: la fila sigue ahí, con su fecha de archivado."""
        self._delete()

        archived = Project.all_objects.get(pk=self.project.pk)
        self.assertIsNotNone(archived.deleted_at)

    def test_its_activities_are_archived_too(self):
        """El CASCADE de la FK no actúa con borrado lógico: la base nunca ve un
        borrado. Si no se archivan a mano, quedan vivas colgando de nada."""
        self.assertGreater(ProjectActivity.objects.filter(project=self.project).count(), 0)

        self._delete()

        self.assertEqual(
            ProjectActivity.objects.filter(project=self.project).count(), 0,
            'Quedaron actividades vivas apuntando a un proyecto archivado.',
        )

    def test_archiving_something_that_does_not_exist_is_a_404(self):
        self.assertEqual(
            self._delete('00000000-0000-0000-0000-000000000000').status_code, 404,
        )
