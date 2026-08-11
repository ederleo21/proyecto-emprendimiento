"""La regla del avance.

El avance no se guarda: se cuenta. Y contarlo tiene tres sutilezas que se
rompen en silencio si alguien las toca sin querer:

1. Una actividad **elegible** no cuenta hasta que alguien la elige.
2. Una actividad **derivada** no se confirma a mano: se marca sola cuando el
   proyecto ya eligió en todas las etapas que admiten elección.
3. Un proyecto sin actividades aplicables da 0, no una división por cero.

Estos tests arman su propio catálogo mínimo en vez de usar `seed_stages`, para
que prueben **la regla** y no los datos. Que el seed real siga siendo coherente
se verifica aparte, en `test_seed.py`.
"""
from django_tenants.test.cases import TenantTestCase

from entrepreneurship.models import Project, ProjectActivity, Stage, StageActivity


class ProgressTests(TenantTestCase):

    def setUp(self):
        # Etapa A: una fija y una derivada.
        self.stage_a = Stage.objects.create(code='STAGE_A', name='Etapa A', order=1)
        self.fixed = StageActivity.objects.create(
            stage=self.stage_a, code='A_FIXED', name='Fija', order=1,
        )
        self.derived = StageActivity.objects.create(
            stage=self.stage_a, code='A_DERIVED', name='Derivada', order=2,
            is_derived=True,
        )

        # Etapa B: dos elegibles. Es la única que admite elección, así que de
        # ella depende `selections_complete`.
        self.stage_b = Stage.objects.create(code='STAGE_B', name='Etapa B', order=2)
        self.opt_one = StageActivity.objects.create(
            stage=self.stage_b, code='B_OPT_ONE', name='Elegible 1', order=1,
            is_optional=True,
        )
        self.opt_two = StageActivity.objects.create(
            stage=self.stage_b, code='B_OPT_TWO', name='Elegible 2', order=2,
            is_optional=True,
        )

        self.project = Project.objects.create(title='Proyecto de prueba')

    # ── Elegibles ────────────────────────────────────────────────────

    def test_optional_activity_does_not_apply_until_chosen(self):
        """Sin elegir, las elegibles no entran en la cuenta."""
        applicable = self.project.applicable_activities()
        self.assertIn(self.fixed, applicable)
        self.assertIn(self.derived, applicable)
        self.assertNotIn(self.opt_one, applicable)
        self.assertNotIn(self.opt_two, applicable)

    def test_optional_activity_applies_once_chosen(self):
        """Elegirla la mete en la cuenta, aunque no esté confirmada."""
        ProjectActivity.objects.create(project=self.project, activity=self.opt_one)

        applicable = self.project.applicable_activities()
        self.assertIn(self.opt_one, applicable)
        self.assertNotIn(self.opt_two, applicable)

    # ── Actividad derivada ───────────────────────────────────────────

    def test_selections_incomplete_while_a_stage_has_no_choice(self):
        self.assertFalse(self.project.selections_complete)

    def test_selections_complete_once_every_stage_chose(self):
        """Basta una elección por etapa: no hay que elegirlas todas."""
        ProjectActivity.objects.create(project=self.project, activity=self.opt_one)
        self.assertTrue(self.project.selections_complete)

    def test_derived_activity_is_not_confirmed_while_selections_are_missing(self):
        self.assertFalse(
            self.project.is_activity_confirmed(self.derived)
        )

    def test_derived_activity_confirms_itself_when_selections_complete(self):
        """Nadie la marcó: se marca sola. Es el corazón de la regla."""
        ProjectActivity.objects.create(project=self.project, activity=self.opt_one)
        self.assertTrue(self.project.is_activity_confirmed(self.derived))

    def test_derived_activity_ignores_its_own_checkbox(self):
        """Aunque la fila diga `is_confirmed=True`, manda el cálculo."""
        ProjectActivity.objects.create(
            project=self.project, activity=self.derived, is_confirmed=True,
        )
        # Todavía falta elegir en la etapa B.
        self.assertFalse(self.project.is_activity_confirmed(self.derived))

    # ── Porcentajes ──────────────────────────────────────────────────

    def test_progress_is_zero_without_confirmations(self):
        self.assertEqual(self.project.progress, 0)

    def test_progress_counts_confirmed_over_applicable(self):
        """Aplicables: fija + derivada = 2. Confirmada: la fija. → 50%."""
        ProjectActivity.objects.create(
            project=self.project, activity=self.fixed, is_confirmed=True,
        )
        self.assertEqual(self.project.progress, 50)

    def test_choosing_an_optional_lowers_progress(self):
        """Elegir suma una aplicable sin sumar una confirmada.

        Aplicables pasa de 2 a 3, y la derivada se confirma sola al elegir:
        confirmadas 2 de 3 → 67%.
        """
        ProjectActivity.objects.create(
            project=self.project, activity=self.fixed, is_confirmed=True,
        )
        self.assertEqual(self.project.progress, 50)

        ProjectActivity.objects.create(project=self.project, activity=self.opt_one)
        self.assertEqual(self.project.progress, 67)

    def test_progress_is_one_hundred_when_everything_applicable_is_confirmed(self):
        ProjectActivity.objects.create(
            project=self.project, activity=self.fixed, is_confirmed=True,
        )
        ProjectActivity.objects.create(
            project=self.project, activity=self.opt_one, is_confirmed=True,
        )
        self.assertEqual(self.project.progress, 100)

    def test_stage_progress_only_counts_its_own_stage(self):
        """La etapa A tiene fija + derivada; confirmar la fija la deja en 50%,
        sin que lo que pase en la B la mueva."""
        ProjectActivity.objects.create(
            project=self.project, activity=self.fixed, is_confirmed=True,
        )
        self.assertEqual(self.project.stage_progress(self.stage_a), 50)
        self.assertEqual(self.project.stage_progress(self.stage_b), 0)

    def test_stage_without_applicable_activities_is_zero_not_a_crash(self):
        """La etapa B solo tiene elegibles: sin elegir, no hay sobre qué
        dividir. Debe dar 0 y no reventar."""
        self.assertEqual(self.project.stage_progress(self.stage_b), 0)

    def test_inactive_activities_are_left_out(self):
        self.fixed.is_active = False
        self.fixed.save(update_fields=['is_active'])

        self.assertNotIn(self.fixed, self.project.applicable_activities())
