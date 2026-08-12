"""Instituciones y sus dominios — `django-tenants`.

Un schema de PostgreSQL por institución. La lista es **réplica**: la fuente de
verdad es el IAM de InnoTech y llega por `sync_tenants`. Acá no se crean
instituciones a mano, salvo para desarrollar sin IAM
(`create_tenant_local`).
"""
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django_tenants.models import DomainMixin, TenantMixin

# Un logotipo institucional no pesa megas. El tope evita que alguien suba la
# foto de un evento por equivocación y la cabecera tarde en cargar.
LOGO_MAX_BYTES = 2 * 1024 * 1024


def validar_peso_logo(archivo):
    if archivo.size > LOGO_MAX_BYTES:
        raise ValidationError(
            f'El logotipo no puede pesar más de {LOGO_MAX_BYTES // 1024 // 1024} MB. '
            f'El archivo pesa {archivo.size // 1024} KB.'
        )

# Los mismos valores que trae el branding de InnoTech por defecto
# (`ui-svelte/branding.ts`). No son la identidad de nadie: son el neutro para
# que la pantalla no salga rota mientras la institución no configure el suyo.
COLOR_POR_DEFECTO = '#349AFE'
COLOR_SECUNDARIO_POR_DEFECTO = '#150089'


class Tenant(TenantMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # El IAM es la fuente de verdad del nombre cuando está conectado:
    # `sync_tenants` lo sobreescribe. Mientras no lo esté, se edita desde la
    # pantalla de identidad visual — si no, un nombre mal escrito al crear la
    # institución quedaría congelado para siempre.
    name = models.CharField(max_length=255)
    subtitle = models.CharField(
        max_length=120,
        default='Vinculación con la Sociedad',
        blank=True,
        help_text='La línea bajo el nombre en la cabecera.',
    )
    logo = models.FileField(
        upload_to='branding/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['png', 'jpg', 'jpeg', 'svg', 'webp'],
                message='El logotipo debe ser PNG, JPG, SVG o WEBP.',
            ),
            validar_peso_logo,
        ],
        help_text='Reemplaza la inicial en la cabecera.',
    )
    primary_color = models.CharField(
        max_length=7,
        default=COLOR_POR_DEFECTO,
        help_text='Color de marca. Sobreescribe la rampa `--ds-brand-*`.',
    )
    secondary_color = models.CharField(
        max_length=7,
        default=COLOR_SECUNDARIO_POR_DEFECTO,
        help_text='Color de apoyo. Sobreescribe la rampa `--ds-info-*`.',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # `schema_name` lo aporta TenantMixin.
    # Crear el schema al guardar: un tenant sin schema no sirve de nada.
    auto_create_schema = True

    class Meta:
        verbose_name = 'Institución'
        verbose_name_plural = 'Instituciones'

    def __str__(self):
        return f'{self.name} ({self.schema_name})'


class Domain(DomainMixin):
    """Host por el que se resuelve el tenant (`itb.localhost`)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.domain
