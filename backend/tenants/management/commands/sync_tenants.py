"""Trae la lista de instituciones desde el IAM de InnoTech.

La fuente de verdad de qué instituciones existen es IAM. Este comando las
replica localmente y crea el schema de cada una.

No borra nada: una institución que desaparezca de IAM se marca inactiva. Borrar
un schema con datos por una respuesta incompleta sería irreversible.

    python manage.py sync_tenants
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core.helpers.service_helper import ServiceHelper
from tenants.models import Domain, Tenant

IAM_TENANTS_ENDPOINT = '/core/api/v1/internal/tenants/'


class Command(BaseCommand):
    help = 'Replica las instituciones desde IAM y crea sus schemas.'

    def handle(self, *args, **options):
        self.stdout.write('Consultando instituciones en IAM...')
        try:
            response = ServiceHelper.call(service_name='IAM', endpoint=IAM_TENANTS_ENDPOINT)
        except Exception as exc:  # noqa: BLE001 — sin IAM se sigue trabajando
            self.stdout.write(self.style.WARNING(
                f'No se pudo consultar IAM ({exc}). '
                f'Para trabajar sin IAM: '
                f'python manage.py create_tenant_local <schema> "<nombre>"'
            ))
            return

        payload = response.get('data', response) if isinstance(response, dict) else response
        if isinstance(payload, dict):
            payload = payload.get('results', [])
        if not isinstance(payload, list):
            self.stdout.write(self.style.ERROR('IAM devolvió algo que no es una lista.'))
            return

        created = updated = 0
        seen = set()

        for item in payload:
            schema_name = (item.get('schema_name') or '').strip()
            if not schema_name or schema_name == 'public':
                continue
            seen.add(schema_name)

            with transaction.atomic():
                tenant, is_new = Tenant.objects.update_or_create(
                    schema_name=schema_name,
                    defaults={
                        'name': item.get('name') or schema_name,
                        'is_active': bool(item.get('is_active', True)),
                    },
                )
                # El dominio permite resolver por Host; el middleware además
                # acepta la cabecera X-Tenant-Schema.
                Domain.objects.get_or_create(
                    domain=f'{schema_name}.localhost',
                    tenant=tenant,
                    defaults={'is_primary': True},
                )

            created += int(is_new)
            updated += int(not is_new)
            self.stdout.write(f'  {schema_name}: {tenant.name}')

        # Marcar inactivas las que ya no llegan, sin borrar su schema.
        missing = Tenant.objects.exclude(schema_name__in=seen).exclude(
            schema_name='public',
        ).filter(is_active=True)
        deactivated = 0
        for tenant in missing:
            tenant.is_active = False
            tenant.save(update_fields=['is_active'])
            deactivated += 1
            self.stdout.write(self.style.WARNING(
                f'  {tenant.schema_name}: ya no está en IAM, inactivada'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'Sync OK: {created} creadas, {updated} actualizadas, {deactivated} inactivadas.'
        ))
