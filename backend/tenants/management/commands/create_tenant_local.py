"""Crea una institución a mano, sin depender de IAM.

Para desarrollar cuando el IAM de InnoTech no está levantado. En un entorno
integrado las instituciones llegan por `sync_tenants`.

    python manage.py create_tenant_local itb "Instituto Tecnológico Bolivariano"
"""
from django.core.management.base import BaseCommand, CommandError

from tenants.models import Domain, Tenant


class Command(BaseCommand):
    help = 'Crea una institución local (desarrollo, sin IAM).'

    def add_arguments(self, parser):
        parser.add_argument('schema', help='Nombre del schema, en minúsculas (ej. itb).')
        parser.add_argument('name', help='Nombre visible de la institución.')

    def handle(self, *args, **options):
        schema_name = options['schema'].strip().lower()
        if not schema_name.isidentifier():
            raise CommandError(
                f'"{schema_name}" no sirve como nombre de schema: solo letras, '
                f'dígitos y guion bajo, y no puede empezar con dígito.'
            )
        if schema_name == 'public':
            raise CommandError('"public" está reservado para las tablas compartidas.')

        tenant, is_new = Tenant.objects.get_or_create(
            schema_name=schema_name,
            defaults={'name': options['name']},
        )
        # `auto_create_schema` crea el schema y corre las migraciones de tenant.

        for host in (f'{schema_name}.localhost', 'localhost'):
            # `localhost` se asigna al primer tenant que lo pida: es el atajo
            # para que el navegador resuelva sin tocar el archivo hosts.
            Domain.objects.get_or_create(
                domain=host, tenant=tenant,
                defaults={'is_primary': host.startswith(schema_name)},
            )

        status = 'creada' if is_new else 'ya existía'
        self.stdout.write(self.style.SUCCESS(
            f'Institución "{tenant.name}" ({schema_name}) {status}.\n'
            f'  Hosts: {schema_name}.localhost, localhost\n'
            f'  Cabecera equivalente: X-Tenant-Schema: {schema_name}'
        ))
