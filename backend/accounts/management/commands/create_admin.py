"""Crea el primer usuario administrador y su membresía.

Sin esto no hay forma de entrar: el servicio no trae usuarios de fábrica.

    python manage.py create_admin admin --password admin123 --schema itb
"""
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Membership, User
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Crea un usuario administrador y lo asocia a una institución.'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('--password', required=True)
        parser.add_argument('--email', default='')
        parser.add_argument(
            '--schema', default='',
            help='Institución a la que pertenece. Sin esto el usuario entra pero no ve datos.',
        )

    def handle(self, *args, **options):
        username = options['username'].strip()
        user = User.objects.filter(username__iexact=username).first()

        if user is None:
            user = User.objects.create_superuser(
                username=username,
                password=options['password'],
                email=options['email'],
            )
            self.stdout.write(self.style.SUCCESS(f'Usuario "{username}" creado.'))
        else:
            # Reejecutar el comando sirve para resetear la contraseña.
            user.set_password(options['password'])
            user.is_superuser = user.is_staff = user.is_active = True
            user.save()
            self.stdout.write(self.style.WARNING(f'Usuario "{username}" ya existía: contraseña actualizada.'))

        schema = options['schema'].strip()
        if schema:
            tenant = Tenant.objects.filter(schema_name=schema).first()
            if tenant is None:
                raise CommandError(
                    f'No existe la institución "{schema}". '
                    f'Créala con: python manage.py create_tenant_local {schema} "<nombre>"'
                )
            _m, created = Membership.objects.get_or_create(
                user=user, tenant=tenant, defaults={'role': 'Administrador'},
            )
            status = 'creada' if created else 'ya existía'
            self.stdout.write(f'  Membresía en "{tenant.name}" {status}.')
        else:
            self.stdout.write(self.style.WARNING(
                '  Sin --schema: el usuario podrá entrar pero no verá datos de ninguna institución.'
            ))
