"""Catálogo de permisos de este servicio.

Mismo formato que `academic_service/permissions.py` en el monorepo de InnoTech:
un identificador de servicio y una lista plana de `(código, módulo, descripción)`
que se registra en el IAM al arrancar.

**Los permisos se declaran acá y no en pantalla, a propósito.** Un permiso
existe porque hay código que lo comprueba; inventar uno desde la interfaz
dejaría una etiqueta que no protege nada, y eso es peor que no tenerla porque
parece seguridad. Los **roles** sí se gestionan desde pantalla: son
combinaciones de estos permisos y cambian sin desplegar.

Para agregar un permiso: se suma acá **y** se usa en la vista que lo exige. Si
no se comprueba en ningún lado, no se agrega.
"""

# Identificador del servicio ante el IAM. No tocar una vez en producción:
# rompería las asignaciones ya hechas. Mismo criterio que `SERVICE_SOURCE` en
# `academic_service`.
SERVICE_SOURCE = 'OUTREACH'

# Los módulos agrupan los permisos en la pantalla de roles. Son etiquetas de
# presentación: lo que manda es el código.
MODULE_PROJECTS = 'Proyectos'
MODULE_ACTIVITIES = 'Actividades'
MODULE_CATALOG = 'Catálogo'
MODULE_SETTINGS = 'Configuración'
MODULE_SECURITY = 'Seguridad'

# (código, módulo, descripción)
SERVICE_PERMISSIONS = [
    # ── Proyectos ────────────────────────────────────────────────────
    ('OUTREACH_PROJECT_VIEW', MODULE_PROJECTS, 'Ver los proyectos de emprendimiento'),
    ('OUTREACH_PROJECT_CREATE', MODULE_PROJECTS, 'Dar de alta un proyecto'),
    ('OUTREACH_PROJECT_EDIT', MODULE_PROJECTS, 'Corregir los datos de un proyecto'),
    ('OUTREACH_PROJECT_ARCHIVE', MODULE_PROJECTS, 'Archivar un proyecto'),
    ('OUTREACH_PROJECT_SET_STAGE', MODULE_PROJECTS, 'Mover un proyecto de etapa'),

    # ── Actividades ──────────────────────────────────────────────────
    #
    # Confirmar y elegir van separados porque son decisiones distintas: elegir
    # arma el plan del proyecto, confirmar declara que algo se hizo.
    ('OUTREACH_ACTIVITY_CONFIRM', MODULE_ACTIVITIES, 'Confirmar una actividad como realizada'),
    ('OUTREACH_ACTIVITY_SELECT', MODULE_ACTIVITIES, 'Elegir qué actividades opcionales aplican'),

    # ── Catálogo del proceso ─────────────────────────────────────────
    ('OUTREACH_CATALOG_VIEW', MODULE_CATALOG, 'Ver las etapas y actividades del proceso'),
    ('OUTREACH_CATALOG_EDIT', MODULE_CATALOG, 'Cambiar las etapas y actividades del proceso'),

    # ── Configuración ────────────────────────────────────────────────
    ('OUTREACH_SETTINGS_VIEW', MODULE_SETTINGS, 'Ver la configuración del módulo'),
    ('OUTREACH_SETTINGS_EDIT', MODULE_SETTINGS, 'Cambiar la configuración del módulo'),
    ('OUTREACH_BRANDING_EDIT', MODULE_SETTINGS, 'Cambiar la identidad visual de la institución'),

    # ── Seguridad ────────────────────────────────────────────────────
    ('OUTREACH_ROLE_VIEW', MODULE_SECURITY, 'Ver los roles y sus permisos'),
    ('OUTREACH_ROLE_EDIT', MODULE_SECURITY, 'Crear roles y cambiar sus permisos'),
    ('OUTREACH_MEMBER_ASSIGN', MODULE_SECURITY, 'Asignar el rol de una persona'),
]

# Los códigos sueltos, para comprobar rápido.
ALL_CODES = frozenset(code for code, _module, _desc in SERVICE_PERMISSIONS)

# El orden en que se muestran los módulos en la pantalla de roles.
MODULE_ORDER = [
    MODULE_PROJECTS,
    MODULE_ACTIVITIES,
    MODULE_CATALOG,
    MODULE_SETTINGS,
    MODULE_SECURITY,
]


def by_module() -> dict:
    """Los permisos agrupados por módulo, en el orden de `MODULE_ORDER`.

    Es la forma que necesita la pantalla: una fila por módulo con sus casillas.
    """
    grouped: dict[str, list] = {module: [] for module in MODULE_ORDER}
    for code, module, description in SERVICE_PERMISSIONS:
        grouped.setdefault(module, []).append(
            {'code': code, 'description': description},
        )
    return grouped
