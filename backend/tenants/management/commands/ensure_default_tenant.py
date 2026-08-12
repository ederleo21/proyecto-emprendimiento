"""Deja lista una institución para poder trabajar, si no hay ninguna.

Corre en cada arranque. La idea es que alguien clone el proyecto, levante el
stack y **tenga algo que ver**, sin buscar en el README qué comando falta.

No pisa nada: si ya hay instituciones —porque `sync_tenants` las trajo del IAM
o porque alguien las creó a mano— no hace absolutamente nada. Solo actúa sobre
una base vacía.

Cuál crea sale de la configuración (`DEFAULT_TENANT_SCHEMA` y
`DEFAULT_TENANT_NAME`), no de un valor escrito acá: cada despliegue es para una
institución distinta.
"""
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Crea la institución por defecto y siembra su catálogo, si no hay ninguna.'

    def handle(self, *args, **options):
        # `public` es el schema de las tablas compartidas, no una institución.
        existing = Tenant.objects.exclude(schema_name='public').count()
        if existing:
            self.stdout.write(
                f'Ya hay {existing} institución(es); no se crea ninguna.'
            )
            return

        schema = (getattr(settings, 'DEFAULT_TENANT_SCHEMA', '') or '').strip().lower()
        if not schema:
            self.stdout.write(self.style.WARNING(
                'No hay instituciones y `DEFAULT_TENANT_SCHEMA` está vacío: '
                'no se crea ninguna. Créala con `create_tenant_local`.'
            ))
            return

        name = (getattr(settings, 'DEFAULT_TENANT_NAME', '') or '').strip() or schema.upper()

        self.stdout.write(f'Base sin instituciones: creando "{name}" ({schema}).')
        call_command('create_tenant_local', schema, name)

        # Sin catálogo, un proyecto nuevo nace sin actividades y la pantalla
        # sale vacía. Sembrarlo es parte de dejar la institución utilizable.
        call_command('tenant_command', 'seed_stages', schema=schema)
