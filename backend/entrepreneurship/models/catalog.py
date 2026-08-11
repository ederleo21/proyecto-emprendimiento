"""Catálogos del Proyecto de Emprendimiento.

Las etapas y sus actividades salen del mockup del proceso. Van como
**catálogo y no como `choices`**: si el proceso gana una etapa o una actividad,
es una fila nueva y no un despliegue.
"""
from django.db import models

from core.my_base import CatalogBase


class Stage(CatalogBase):
    """Etapa del proceso de emprendimiento."""

    order = models.PositiveSmallIntegerField(
        default=0,
        db_index=True,
        help_text='Posición en el proceso. Define el orden en pantalla.',
    )
    # El color vive en el catálogo y no en el frontend: las tarjetas de
    # métricas lo leen de acá, así una etapa nueva llega con su color puesto.
    color = models.CharField(
        max_length=20,
        default='blue',
        help_text='Color de la tarjeta de métrica: blue, darkblue, orange, red, green.',
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Etapa de Emprendimiento'
        verbose_name_plural = 'Etapas de Emprendimiento'
        db_table = 'ent_stage'
        ordering = ['order', 'code']


class StageActivity(CatalogBase):
    """Actividad que compone una etapa.

    De aquí sale el avance: el porcentaje de una etapa es cuántas de sus
    actividades están confirmadas.

    Hay dos clases, y la diferencia viene del mockup:

    - **Fijas** (`is_optional=False`) — aplican a todo proyecto. Es el caso de
      Idea, Pre-incubación y Pitch, y de "Monitoreo al proyecto" dentro de
      Incubación.
    - **Elegibles** (`is_optional=True`) — se escogen por proyecto. Un
      emprendimiento puede llevar Bootcamp y Mentorías y otro no. Solo cuentan
      para el avance las que se hayan elegido.
    """

    stage = models.ForeignKey(
        'entrepreneurship.Stage',
        on_delete=models.PROTECT,
        related_name='activities',
    )
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_optional = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            'Si es verdadero, la actividad se elige por proyecto y solo cuenta '
            'para el avance cuando fue elegida. Si es falso, aplica siempre.'
        ),
    )
    is_derived = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            'Si es verdadero, la actividad NO se confirma a mano: se marca sola '
            'cuando el proyecto ya eligió actividades en todas las etapas que '
            'admiten elección. Es el caso de "Formulación de la Idea", donde '
            'justamente se hacen esas elecciones.'
        ),
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Actividad de Etapa'
        verbose_name_plural = 'Actividades de Etapa'
        db_table = 'ent_stage_activity'
        ordering = ['stage', 'order', 'code']

    def __str__(self):
        return f'{self.stage.name} · {self.name}'
