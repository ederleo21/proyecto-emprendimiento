"""Parámetros del módulo, por institución.

Una sola fila por institución: es el lugar donde vive lo que hoy tendría que
estar escrito a mano en el código. Si mañana una institución quiere que sus
proyectos se llamen `EMP-0001` en vez de `PE-2026-001`, lo cambia desde
pantalla y nadie despliega nada.

Es la misma idea que `CatalogBase` documenta para los catálogos: el
comportamiento del dominio va como dato, no como `if`.

Los `default` de abajo **no son configuración escrita a fuego**: son el valor
con el que nace una institución que todavía no configuró nada. Cualquiera de
ellos se cambia sin tocar el código.
"""
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from core.my_base import BaseModel


class Configuration(BaseModel):
    """Configuración del Proyecto de Emprendimiento para esta institución."""

    # ── Código del proyecto ──────────────────────────────────────────
    #
    # Con estos tres campos se arma el código legible: prefijo, año opcional y
    # cuántos dígitos lleva el correlativo.

    project_code_prefix = models.CharField(
        max_length=10,
        default='PE',
        validators=[RegexValidator(
            regex=r'^[A-Z][A-Z0-9-]*$',
            message='El prefijo debe empezar con letra mayúscula y solo admite '
                    'mayúsculas, dígitos y guion.',
        )],
        help_text='Letras con las que empieza el código. Ejemplo: PE → PE-2026-001',
    )
    project_code_include_year = models.BooleanField(
        default=True,
        help_text='Si el código lleva el año. Con año: PE-2026-001. Sin año: PE-001.',
    )
    project_code_digits = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        help_text='Cuántos dígitos tiene el correlativo. 3 → 001, 4 → 0001.',
    )

    class Meta:
        verbose_name = 'Configuración de Emprendimiento'
        verbose_name_plural = 'Configuración de Emprendimiento'
        db_table = 'ent_configuration'

    # ── Acceso ───────────────────────────────────────────────────────

    @classmethod
    def load(cls) -> 'Configuration':
        """La configuración de esta institución, creándola si es la primera vez.

        Se llama sin argumentos porque el schema del tenant ya está fijado por
        el middleware: dentro de un request siempre hay una sola.
        """
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj

    # ── Código del proyecto ──────────────────────────────────────────

    def code_prefix(self, year: int) -> str:
        """La parte fija del código, hasta antes del correlativo."""
        if self.project_code_include_year:
            return f'{self.project_code_prefix}-{year}-'
        return f'{self.project_code_prefix}-'

    def format_code(self, year: int, number: int) -> str:
        return f'{self.code_prefix(year)}{number:0{self.project_code_digits}d}'

    def __str__(self):
        return f'Configuración ({self.project_code_prefix})'
