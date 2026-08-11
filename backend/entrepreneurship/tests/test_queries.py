"""Que el listado no vuelva a hacer una consulta por proyecto.

El avance se calcula recorriendo el catálogo y lo que el proyecto tiene
marcado. Es fácil escribirlo de forma que cada fila consulte por su cuenta:
con 10 proyectos no se nota, con 300 sí.

Estos tests no miran un número mágico de consultas — miran que **no crezca**
al agregar proyectos. Un número fijo se rompería con cualquier cambio inocente
de `select_related`; esto solo se rompe si vuelve el N+1.
"""
from io import StringIO

from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django_tenants.test.cases import TenantTestCase

from entrepreneurship.models import Project, ProjectActivity, StageActivity


class ListQueryCountTests(TenantTestCase):

    def setUp(self):
        call_command('seed_stages', stdout=StringIO())
        self.fixed = list(StageActivity.objects.filter(is_optional=False, is_active=True))

    def _create_projects(self, how_many):
        for i in range(how_many):
            project = Project.objects.create(title=f'Proyecto {i}')
            ProjectActivity.objects.bulk_create([
                ProjectActivity(project=project, activity=a) for a in self.fixed
            ])

    def _queries_to_list_everything(self) -> int:
        """Repite lo que hace `ProjectListCreateView.get`."""
        with CaptureQueriesContext(connection) as captured:
            rows = list(
                Project.objects
                .select_related('stage')
                .prefetch_related('activities__activity')
            )
            Project.share_catalog(rows)
            for row in rows:
                row.progress
        return len(captured)

    def test_query_count_does_not_grow_with_the_number_of_projects(self):
        self._create_projects(1)
        with_one = self._queries_to_list_everything()

        self._create_projects(9)
        with_ten = self._queries_to_list_everything()

        self.assertEqual(
            with_one, with_ten,
            f'El listado pasó de {with_one} a {with_ten} consultas al pasar de '
            f'1 a 10 proyectos: volvió el N+1.',
        )

    def test_progress_is_still_right_after_sharing_the_catalog(self):
        """Compartir el catálogo es una optimización: no puede cambiar el
        resultado."""
        self._create_projects(3)

        rows = list(Project.objects.prefetch_related('activities__activity'))
        shared = [p.progress for p in Project.share_catalog(rows)]

        alone = [
            Project.objects.get(pk=p.pk).progress
            for p in rows
        ]
        self.assertEqual(shared, alone)


class StaleCacheTests(TenantTestCase):
    """Con `prefetch_related`, la lista de actividades queda congelada.

    Si se lee el avance después de tocar la base sin volver a leer el proyecto,
    devuelve el porcentaje anterior. Es el error que evita `_reloaded()` en la
    vista que marca actividades.
    """

    def setUp(self):
        call_command('seed_stages', stdout=StringIO())
        self.project = Project.objects.create(title='Proyecto')
        ProjectActivity.objects.bulk_create([
            ProjectActivity(project=self.project, activity=a)
            for a in StageActivity.objects.filter(is_optional=False, is_active=True)
        ])

    def test_reloading_reflects_a_confirmation_made_afterwards(self):
        stale = Project.objects.prefetch_related('activities__activity').get(pk=self.project.pk)
        before = stale.progress

        activity = StageActivity.objects.get(code='IDEA_CALL')
        ProjectActivity.objects.filter(
            project=self.project, activity=activity,
        ).update(is_confirmed=True)

        # El objeto viejo sigue viendo lo de antes: eso es esperable.
        self.assertEqual(stale.progress, before)

        # El releído tiene que ver el cambio.
        fresh = Project.objects.prefetch_related('activities__activity').get(pk=self.project.pk)
        self.assertGreater(fresh.progress, before)
