"""Invariantes del catálogo sembrado.

`test_progress.py` prueba la regla con un catálogo inventado. Estos prueban que
**el catálogo real la siga cumpliendo**, que es lo que se rompe cuando alguien
agrega una etapa o cambia una bandera sin saber qué dependía de ella.

Cada test dice qué se rompería si el seed cambiara.
"""
from io import StringIO

from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase

from entrepreneurship.models import Stage, StageActivity


class SeedInvariantTests(TenantTestCase):

    def setUp(self):
        call_command('seed_stages', stdout=StringIO())

    def test_seeds_the_five_stages_of_the_process(self):
        self.assertEqual(Stage.objects.count(), 5)

    def test_there_is_exactly_one_derived_activity(self):
        """Si aparece una segunda derivada, las dos se marcarían con la misma
        condición y ninguna de las dos podría confirmarse a mano. Hoy la única
        es "Formulación de la Idea"."""
        derived = StageActivity.objects.filter(is_derived=True)
        self.assertEqual(derived.count(), 1)
        self.assertEqual(derived.first().code, 'IDEA_FORMULATION')

    def test_the_derived_activity_is_not_optional(self):
        """Derivada y elegible a la vez es una contradicción: tendría que ser
        elegida para aplicar, pero se marca sola por haber elegido."""
        derived = StageActivity.objects.get(is_derived=True)
        self.assertFalse(derived.is_optional)

    def test_the_derived_activity_lives_in_a_stage_without_optionals(self):
        """Si estuviera en una etapa con elegibles, dependería de que alguien
        elija en su propia etapa para marcarse. Hoy vive en Idea, que no las
        tiene."""
        derived = StageActivity.objects.get(is_derived=True)
        self.assertFalse(
            StageActivity.objects.filter(
                stage=derived.stage, is_optional=True, is_active=True,
            ).exists()
        )

    def test_at_least_one_stage_admits_choosing(self):
        """Sin ninguna elegible, `selections_complete` daría siempre True y la
        actividad derivada nacería confirmada. La regla quedaría muerta."""
        stages_with_optionals = (
            Stage.objects
            .filter(activities__is_optional=True, activities__is_active=True)
            .distinct()
        )
        self.assertGreaterEqual(stages_with_optionals.count(), 1)

    def test_codes_are_in_english(self):
        """Los `code` son identificadores y viajan en la URL de la pantalla de
        etapa. Los `name`, que sí se leen en pantalla, siguen en español."""
        self.assertTrue(Stage.objects.filter(code='PRE_INCUBATION').exists())
        self.assertTrue(StageActivity.objects.filter(code='INC_MENTORING').exists())
        # Y el nombre visible no se tradujo.
        self.assertEqual(
            Stage.objects.get(code='PRE_INCUBATION').name, 'Pre-incubación',
        )

    def test_running_the_seed_twice_does_not_duplicate(self):
        """El comando dice ser idempotente. Si deja de serlo, cada despliegue
        duplicaría el catálogo."""
        stages = Stage.objects.count()
        activities = StageActivity.objects.count()

        call_command('seed_stages', stdout=StringIO())

        self.assertEqual(Stage.objects.count(), stages)
        self.assertEqual(StageActivity.objects.count(), activities)
