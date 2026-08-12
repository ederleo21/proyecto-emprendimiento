"""Siembra los roles del proceso de emprendimiento.

Salen de los carriles del diagrama de vinculación. Van como comando y no como
migración porque son **datos del negocio**: cuando el proceso gane o pierda un
rol, se vuelve a sembrar sin tocar el historial de migraciones.

Idempotente por `code`: no pisa los permisos que la institución haya ajustado
desde pantalla, solo crea lo que falte.

    python manage.py seed_roles
"""
from django.core.management.base import BaseCommand

from accounts.models import Role, RolePermission
from permissions import ALL_CODES

# ── Los roles del diagrama ───────────────────────────────────────────
#
# El `scope` los separa en dos, y la distinción no es cosmética:
#
#   INSTITUTIONAL — se es siempre. El Director de Emprendimiento lo es en todo
#                   proyecto, así que los permisos de módulo le aplican.
#   PROJECT       — se es de un proyecto concreto. Kevin es el emprendedor del
#                   suyo, no de todos. Un permiso global de "editar proyectos"
#                   no significa nada acá: eso lo resolverá la tabla que ate
#                   persona + rol + proyecto.
#
# La clasificación de abajo es una **propuesta**, hecha leyendo los nombres. Se
# ajusta desde pantalla cuando llegue el diagrama con sus carriles.
#
# (code, name, scope, permisos por defecto)
ROLES = [
    # Cargos en la institución
    ('ENTREPRENEURSHIP_DIRECTOR', 'Director de Emprendimiento', 'INSTITUTIONAL', 'gestion'),
    ('ENTREPRENEURSHIP_ASSISTANT', 'Auxiliar de Emprendimiento', 'INSTITUTIONAL', 'operacion'),
    ('ENTREPRENEURSHIP_COMMITTEE', 'Comité de Emprendimiento', 'INSTITUTIONAL', 'revision'),
    ('INSTITUTIONAL_COMMITTEE', 'Comité Institucional', 'INSTITUTIONAL', 'revision'),
    ('OUTREACH_DIRECTOR', 'Director de Vinculación', 'INSTITUTIONAL', 'gestion'),
    ('APPROVING_AUTHORITY', 'Autoridad Aprobatoria', 'INSTITUTIONAL', 'revision'),
    ('FINANCIAL_REVIEWER', 'Revisor Financiero', 'INSTITUTIONAL', 'revision'),
    ('COORDINATOR', 'Coordinador', 'INSTITUTIONAL', 'operacion'),
    ('TEACHER', 'Docente', 'INSTITUTIONAL', 'consulta'),

    # Papeles dentro de un proyecto
    ('PROJECT_DIRECTOR', 'Director de Proyecto', 'PROJECT', 'consulta'),
    ('ENTREPRENEUR', 'Emprendedor', 'PROJECT', 'consulta'),
    ('AUTHOR_TEACHER', 'Docente Autor', 'PROJECT', 'consulta'),
    ('PRESENTER', 'Expositor', 'PROJECT', 'consulta'),
    ('FACILITATOR', 'Facilitador', 'PROJECT', 'consulta'),
    ('INSTRUCTOR', 'Instructor', 'PROJECT', 'consulta'),
    ('PARTICIPANT', 'Participante', 'PROJECT', 'consulta'),
]

# ── Los repartos de permisos ─────────────────────────────────────────
#
# Son un punto de partida razonable, no la verdad: quién puede confirmar una
# actividad es justo lo que el proceso todavía no define. Se ajustan desde
# pantalla.
CONSULTA = [
    'OUTREACH_PROJECT_VIEW',
    'OUTREACH_CATALOG_VIEW',
]
OPERACION = CONSULTA + [
    'OUTREACH_PROJECT_CREATE',
    'OUTREACH_PROJECT_EDIT',
    'OUTREACH_ACTIVITY_CONFIRM',
    'OUTREACH_ACTIVITY_SELECT',
]
REVISION = CONSULTA + [
    'OUTREACH_ACTIVITY_CONFIRM',
]
GESTION = OPERACION + [
    'OUTREACH_PROJECT_ARCHIVE',
    'OUTREACH_PROJECT_SET_STAGE',
    'OUTREACH_SETTINGS_VIEW',
    'OUTREACH_MEMBER_ASSIGN',
]

REPARTOS = {
    'consulta': CONSULTA,
    'operacion': OPERACION,
    'revision': REVISION,
    'gestion': GESTION,
}


class Command(BaseCommand):
    help = 'Siembra los roles del proceso de emprendimiento.'

    def handle(self, *args, **options):
        creados = existentes = 0

        for code, name, scope, reparto in ROLES:
            role, is_new = Role.objects.get_or_create(
                code=code,
                defaults={'name': name, 'scope': scope},
            )
            creados += int(is_new)
            existentes += int(not is_new)

            # Los permisos solo se ponen al crear: si la institución los ajustó
            # desde pantalla, resembrar no puede deshacerle el trabajo.
            if is_new:
                for permiso in REPARTOS[reparto]:
                    # Se comprueba contra el catálogo para que una errata acá
                    # no cree un permiso fantasma que nadie comprueba nunca.
                    if permiso not in ALL_CODES:
                        self.stdout.write(self.style.ERROR(
                            f'  "{permiso}" no está en el catálogo de permisos; se omite.'
                        ))
                        continue
                    RolePermission.objects.get_or_create(role=role, code=permiso)

            marca = 'cargo' if scope == 'INSTITUTIONAL' else 'por proyecto'
            estado = 'creado' if is_new else 'ya existía'
            self.stdout.write(f'  {name:<32} ({marca}) — {estado}')

        self.stdout.write(self.style.SUCCESS(
            f'Roles: creados={creados} existentes={existentes}'
        ))
