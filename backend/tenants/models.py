"""Instituciones y sus dominios — `django-tenants`.

Un schema de PostgreSQL por institución. La lista es **réplica**: la fuente de
verdad es el IAM de InnoTech y llega por `sync_tenants`. Acá no se crean
instituciones a mano, salvo para desarrollar sin IAM
(`create_tenant_local`).
"""
import uuid

from django.db import models
from django_tenants.models import DomainMixin, TenantMixin

# Los mismos valores que trae el branding de InnoTech por defecto
# (`ui-svelte/branding.ts`). No son la identidad de nadie: son el neutro para
# que la pantalla no salga rota mientras la institución no configure el suyo.
COLOR_POR_DEFECTO = '#349AFE'
COLOR_SECUNDARIO_POR_DEFECTO = '#150089'


class Tenant(TenantMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
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
