"""Modelos base del servicio.

Espejo reducido de `core_shared.my_base` del monorepo de InnoTech. Las firmas
son idénticas a propósito: si este servicio se integra allá, se cambia el
import y el dominio no se entera.
"""
import uuid

from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Manager por defecto: oculta lo borrado lógicamente."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    """PK UUID, auditoría y borrado lógico.

    El borrado es lógico, así que **una restricción de unicidad nunca debe ir
    en el campo** (`unique=True`): una fila borrada seguiría ocupando el valor.
    Va como `UniqueConstraint` parcial sobre `deleted_at__isnull=True`.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # UUID y no FK: este servicio no tiene tabla de usuarios — la identidad
    # vive en el JWT que emite el IAM.
    created_by = models.UUIDField(null=True, blank=True, editable=False)
    updated_by = models.UUIDField(null=True, blank=True)
    deleted_by = models.UUIDField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, user_id=None, **kwargs):
        """Marca la fila como eliminada sin borrarla."""
        self.deleted_at = timezone.now()
        if user_id:
            self.deleted_by = user_id
        self.save(update_fields=['deleted_at', 'deleted_by', 'updated_at'])

    def hard_delete(self, **kwargs):
        """Eliminación física. Para limpieza y tests, no para el flujo normal."""
        super().delete(**kwargs)


class BasePerson(BaseModel):
    """Datos de una persona. Se reusa en réplicas de otros servicios."""

    document_type = models.CharField(max_length=20)
    document_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class CatalogBase(BaseModel):
    """Base de los catálogos: `code` en MAYÚSCULAS + `name` legible.

    Los catálogos llevan el **comportamiento** del dominio como columnas
    (banderas, plazos), no como `if` en el código: así una figura nueva se
    agrega desde la pantalla sin desplegar.
    """

    from django.core.validators import RegexValidator

    CODE_VALIDATOR = RegexValidator(
        regex=r'^[A-Z][A-Z0-9_-]*$',
        message=(
            'El código debe empezar con letra mayúscula y sólo puede contener '
            'mayúsculas, dígitos, guion bajo (_) y guion (-).'
        ),
        code='invalid_catalog_code',
    )

    code = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        validators=[CODE_VALIDATOR],
        help_text='Identificador único en MAYÚSCULAS, sin espacios.',
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        help_text='Etiqueta legible mostrada al usuario.',
    )

    class Meta:
        abstract = True
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.name}'
