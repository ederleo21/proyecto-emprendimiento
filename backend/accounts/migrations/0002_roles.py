"""Roles con permisos, y `Membership.role` deja de ser texto.

El cambio de texto a relación no se puede hacer de un tirón: la columna guarda
`'Administrador'` y convertir eso a un identificador falla. Va en cuatro pasos,
conservando lo que había:

    1. el texto se aparta a `legacy_role`
    2. se crean las tablas de roles y se agrega la relación, vacía
    3. cada membresía se engancha al rol que corresponde a su texto
    4. se retira la columna vieja

Se siembran solo los dos roles que hacen falta para no dejar a nadie fuera:
Administrador —con todo— y uno de solo lectura. Los del proceso los siembra
`seed_roles`, que es un comando y no una migración: son datos del negocio y se
resiembran cuando cambien.
"""
import uuid

import django.db.models.deletion
from django.db import migrations, models


def enganchar_roles(apps, schema_editor):
    """Cada membresía pasa a apuntar al rol con su nombre.

    Si el texto no coincide con ninguno se crea el rol, para no perder lo que
    alguien había escrito a mano.
    """
    Role = apps.get_model('accounts', 'Role')
    RolePermission = apps.get_model('accounts', 'RolePermission')
    Membership = apps.get_model('accounts', 'Membership')

    # Se importa acá y no arriba: una migración tiene que poder correr aunque
    # el catálogo cambie después.
    from permissions import SERVICE_PERMISSIONS

    admin, _ = Role.objects.get_or_create(
        code='ADMIN',
        defaults={
            'name': 'Administrador',
            'description': 'Acceso completo al módulo.',
            'scope': 'INSTITUTIONAL',
            'is_system': True,
        },
    )
    for code, _module, _desc in SERVICE_PERMISSIONS:
        RolePermission.objects.get_or_create(role=admin, code=code)

    lector, _ = Role.objects.get_or_create(
        code='VIEWER',
        defaults={
            'name': 'Consulta',
            'description': 'Solo puede mirar.',
            'scope': 'INSTITUTIONAL',
            'is_system': True,
        },
    )
    for code in ('OUTREACH_PROJECT_VIEW', 'OUTREACH_CATALOG_VIEW',
                 'OUTREACH_SETTINGS_VIEW'):
        RolePermission.objects.get_or_create(role=lector, code=code)

    for membership in Membership.objects.exclude(legacy_role=''):
        nombre = membership.legacy_role.strip()
        rol = Role.objects.filter(name__iexact=nombre).first()
        if rol is None:
            rol = Role.objects.create(
                code=nombre.upper().replace(' ', '_')[:60],
                name=nombre,
                description='Venía del texto libre anterior.',
                scope='INSTITUTIONAL',
            )
        membership.role = rol
        membership.save(update_fields=['role'])


def desenganchar_roles(apps, schema_editor):
    """Devuelve el nombre del rol a la columna de texto."""
    Membership = apps.get_model('accounts', 'Membership')
    for membership in Membership.objects.select_related('role').exclude(role=None):
        membership.legacy_role = membership.role.name
        membership.save(update_fields=['legacy_role'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # 1. El texto se aparta.
        migrations.RenameField(
            model_name='membership', old_name='role', new_name='legacy_role',
        ),

        # 2. Las tablas nuevas.
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(db_index=True, help_text='Identificador estable. En MAYÚSCULAS, sin espacios.', max_length=60, unique=True)),
                ('name', models.CharField(help_text='Como se lee en pantalla.', max_length=120)),
                ('description', models.CharField(blank=True, default='', max_length=255)),
                ('scope', models.CharField(choices=[('INSTITUTIONAL', 'Cargo en la institución'), ('PROJECT', 'Papel dentro de un proyecto')], db_index=True, default='INSTITUTIONAL', max_length=20)),
                ('is_system', models.BooleanField(default=False, help_text='Viene con el sistema. No se puede eliminar.')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Rol',
                'verbose_name_plural': 'Roles',
                'db_table': 'acc_role',
                'ordering': ['scope', 'name'],
            },
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(db_index=True, max_length=60)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='accounts.role')),
            ],
            options={
                'verbose_name': 'Permiso del rol',
                'verbose_name_plural': 'Permisos del rol',
                'db_table': 'acc_role_permission',
                'constraints': [models.UniqueConstraint(fields=('role', 'code'), name='acc_role_permission_unique')],
            },
        ),
        migrations.AddField(
            model_name='membership',
            name='role',
            field=models.ForeignKey(blank=True, help_text='Sin rol, la persona entra pero no puede hacer nada.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='memberships', to='accounts.role'),
        ),

        # 3. Lo guardado se engancha.
        migrations.RunPython(enganchar_roles, desenganchar_roles),

        # 4. La columna vieja se retira.
        migrations.RemoveField(model_name='membership', name='legacy_role'),
    ]
