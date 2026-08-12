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

        # El propio: siempre.
        propio = f'{schema_name}.localhost'
        Domain.objects.get_or_create(
            domain=propio, tenant=tenant, defaults={'is_primary': True},
        )

        # `localhost` a secas es el atajo para no tocar el archivo hosts de
        # Windows, y solo puede apuntar a una institución. Se lo queda la
        # primera que lo pida; las siguientes usan el suyo. Antes se intentaba
        # asignar siempre y la segunda institución reventaba.
        atajo = Domain.objects.filter(domain='localhost').first()
        if atajo is None:
            Domain.objects.create(domain='localhost', tenant=tenant, is_primary=False)
            atajo_de = schema_name
        else:
            atajo_de = atajo.tenant.schema_name

        hosts = propio if atajo_de != schema_name else f'{propio}, localhost'
        status = 'creada' if is_new else 'ya existía'

        self.stdout.write(self.style.SUCCESS(
            f'Institución "{tenant.name}" ({schema_name}) {status}.\n'
            f'  Hosts: {hosts}\n'
            f'  Cabecera equivalente: X-Tenant-Schema: {schema_name}'
        ))
        if atajo_de != schema_name:
            self.stdout.write(self.style.WARNING(
                f'  Ojo: "localhost" a secas resuelve a "{atajo_de}". '
                f'Para entrar a esta usa {propio} o la cabecera.'
            ))
