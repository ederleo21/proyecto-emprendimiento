"""Proyecto de Emprendimiento y su avance.

El avance **no se escribe a mano**: sale de contar cuántas actividades están
confirmadas sobre cuántas aplican. Es la regla del mockup
(`peStageProgress`), no una invención.

Lo que todavía NO está modelado, porque nadie lo ha definido: quién puede
confirmar una actividad, qué entregable exige cada una, y si hay que terminar
una etapa para abrir la siguiente.
"""
from django.db import models
from django.db.models import Q

from core.my_base import BaseModel


class Project(BaseModel):
    """Un proyecto de emprendimiento y la etapa en la que va."""

    # Sin `unique=True`: BaseModel borra en lógico y una fila borrada seguiría
    # ocupando el código. La unicidad va como constraint parcial.
    code = models.CharField(
        max_length=30,
        db_index=True,
        blank=True,
        default='',
        help_text='Identificador legible del proyecto.',
    )
    title = models.TextField(
        help_text='Título del proyecto. En el formulario es un textarea: '
                  'admite el contexto o la motivación institucional.',
    )
    stage = models.ForeignKey(
        'entrepreneurship.Stage',
        on_delete=models.PROTECT,
        related_name='projects',
        null=True,
        blank=True,
        help_text='Etapa actual. Nula mientras no arranque el proceso.',
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Proyecto de Emprendimiento'
        verbose_name_plural = 'Proyectos de Emprendimiento'
        db_table = 'ent_project'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['code'],
                condition=Q(deleted_at__isnull=True) & ~Q(code=''),
                name='ent_project_unique_code_alive',
            ),
        ]

    # ── Avance ───────────────────────────────────────────────────────
    #
    # Todo el cálculo trabaja sobre dos listas ya cargadas: el catálogo de
    # actividades y lo que el proyecto tiene marcado. Se filtran en memoria y
    # no con `.filter()`, porque un `.filter()` sobre el related manager
    # **ignora el `prefetch_related`** y dispara una consulta nueva cada vez.
    # En un listado eso es una consulta por proyecto y por llamada.

    @classmethod
    def share_catalog(cls, projects):
        """Carga el catálogo una vez y se lo presta a todos los proyectos.

        Lo usa el listado: sin esto cada proyecto pide el catálogo por su
        cuenta y con 300 proyectos son 300 consultas idénticas.
        """
        from entrepreneurship.models import StageActivity

        catalog = list(StageActivity.objects.filter(is_active=True))
        for project in projects:
            project._catalog = catalog
        return projects

    def _activity_catalog(self):
        """Catálogo de actividades activas. Se recuerda por instancia."""
        from entrepreneurship.models import StageActivity

        catalog = getattr(self, '_catalog', None)
        if catalog is None:
            catalog = list(StageActivity.objects.filter(is_active=True))
            self._catalog = catalog
        return catalog

    def _chosen_activity_ids(self) -> set:
        """Ids de las elegibles que este proyecto escogió."""
        return {
            pa.activity_id for pa in self.activities.all()
            if pa.activity.is_optional
        }

    def applicable_activities(self, stage=None):
        """Actividades que cuentan para este proyecto.

        Las fijas cuentan siempre. Las elegibles solo si alguien las eligió,
        es decir si existe su fila en `ProjectActivity`.
        """
        chosen = self._chosen_activity_ids()
        return [
            a for a in self._activity_catalog()
            if (stage is None or a.stage_id == stage.id)
            and (not a.is_optional or a.id in chosen)
        ]

    @property
    def selections_complete(self) -> bool:
        """True si el proyecto ya eligió actividades en todas las etapas que
        admiten elección.

        De esto depende la actividad derivada: mientras falte elegir en alguna
        etapa, "Formulación de la Idea" sigue pendiente.
        """
        stages_with_optionals = {
            a.stage_id for a in self._activity_catalog() if a.is_optional
        }
        chosen_stages = {
            pa.activity.stage_id for pa in self.activities.all()
            if pa.activity.is_optional
        }
        return stages_with_optionals <= chosen_stages

    def is_activity_confirmed(self, activity, state=None) -> bool:
        """Si una actividad cuenta como hecha.

        Una actividad derivada no mira su casilla: se calcula. El resto lee la
        marca que dejó quien la confirmó.
        """
        if activity.is_derived:
            return self.selections_complete
        pa = state.get(activity.id) if state is not None else (
            self.activities.filter(activity=activity).first()
        )
        return bool(pa and pa.is_confirmed)

    def _percentage(self, applicable) -> int:
        if not applicable:
            return 0
        state = {pa.activity_id: pa for pa in self.activities.all()}
        done = sum(1 for a in applicable if self.is_activity_confirmed(a, state))
        return round(done / len(applicable) * 100)

    def stage_progress(self, stage) -> int:
        """Porcentaje de avance de una etapa: confirmadas sobre aplicables."""
        return self._percentage(self.applicable_activities(stage))

    @property
    def progress(self) -> int:
        """Avance global: sobre todas las actividades aplicables del proyecto."""
        return self._percentage(self.applicable_activities())

    def __str__(self):
        label = self.title[:60] if self.title else '(sin título)'
        return f'{self.code} · {label}' if self.code else label


class ProjectActivity(BaseModel):
    """Estado de una actividad dentro de un proyecto.

    La fila existe cuando la actividad **aplica** al proyecto:

    - Actividad fija → la fila se crea al dar de alta el proyecto.
    - Actividad elegible → la fila se crea cuando alguien la elige.

    Que exista no significa que esté hecha: eso lo dice `is_confirmed`, que es
    la casilla del checklist en pantalla.
    """

    project = models.ForeignKey(
        'entrepreneurship.Project',
        on_delete=models.CASCADE,
        related_name='activities',
    )
    activity = models.ForeignKey(
        'entrepreneurship.StageActivity',
        on_delete=models.PROTECT,
        related_name='project_activities',
    )
    is_confirmed = models.BooleanField(default=False, db_index=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Actividad del Proyecto'
        verbose_name_plural = 'Actividades del Proyecto'
        db_table = 'ent_project_activity'
        ordering = ['activity__stage__order', 'activity__order']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'activity'],
                condition=Q(deleted_at__isnull=True),
                name='ent_project_activity_unique_alive',
            ),
        ]

    def __str__(self):
        mark = '✓' if self.is_confirmed else '·'
        return f'{mark} {self.activity.name}'
