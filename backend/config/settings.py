"""Configuración del servicio Outreach (Vinculación con la Sociedad).

Sigue las convenciones de los microservicios de InnoTech: multi-tenant por
schema, JWT emitido por IAM (sin tabla de usuarios propia) y respuestas con
envoltorio. Ver el README para el detalle de por qué.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['*']),
    CORS_ALLOWED_ORIGINS=(list, []),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='dev-inseguro-cambiar-en-produccion')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ──────────────────────────────────────────────────────────
# Apps. `django-tenants` separa las que viven en el schema
# público de las que se replican en cada institución.
# ──────────────────────────────────────────────────────────

SHARED_APPS = [
    'django_tenants',
    # `tenants` va acá obligatoriamente: es el registro de instituciones.
    'tenants',
    'django.contrib.contenttypes',
    # `auth` hace falta aunque este servicio NO tenga login propio: DRF importa
    # sus modelos (AnonymousUser, Permission) al cargar. Las tablas quedan
    # vacías — la identidad viaja en el JWT de IAM. Mismo caso en los demás
    # microservicios de InnoTech.
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'core',
    # Usuarios propios: este servicio no depende de que el IAM de InnoTech
    # esté levantado. El token que emite lleva los mismos claims, así que
    # integrarlo después es cambiar la clave de firma. Van en SHARED_APPS
    # (schema público) porque una persona puede pertenecer a más de una
    # institución.
    'accounts',
]

AUTH_USER_MODEL = 'accounts.User'

TENANT_APPS = [
    'django.contrib.contenttypes',
    # Proyecto de Emprendimiento: convocatoria, idea, pre-incubación,
    # incubación, pitch y post-incubación. Cada institución tiene los suyos,
    # aislados en su propio schema.
    'entrepreneurship',
]

INSTALLED_APPS = list(dict.fromkeys(SHARED_APPS + TENANT_APPS))

TENANT_MODEL = 'tenants.Tenant'
TENANT_DOMAIN_MODEL = 'tenants.Domain'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # Antes que nada: el resto del stack asume que el schema ya está fijado.
    'tenants.middleware.RobustTenantMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': []},
}]

# ──────────────────────────────────────────────────────────
# Base de datos — motor de django-tenants, no el de Postgres
# ──────────────────────────────────────────────────────────

DATABASES = {'default': env.db(
    'DATABASE_URL',
    default='postgres://postgres:postgres@db:5432/outreach',
)}
DATABASES['default']['ENGINE'] = 'django_tenants.postgresql_backend'
DATABASE_ROUTERS = ['django_tenants.routers.TenantSyncRouter']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────────────────────
# API
# ──────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Sin tabla auth_user: la identidad viaja en el JWT que emite IAM.
    #
    # `DevAuthentication` va al final: solo actúa si no llegó ninguna
    # credencial real Y `DEV_AUTH_BYPASS` está activo Y `DEBUG=True`.
    # Mientras el servicio no tenga pantalla de acceso, es lo que permite
    # trabajar el frontend.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentication.ServiceJWTAuthentication',
        'core.authentication.DevAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Outreach — Vinculación con la Sociedad',
    'DESCRIPTION': 'Microservicio de vinculación con la sociedad.',
    'VERSION': '0.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ──────────────────────────────────────────────────────────
# Integración con InnoTech
# ──────────────────────────────────────────────────────────

# Debe ser la MISMA que usa IAM para firmar, o sus tokens no validarán acá.
JWT_SIGNING_KEY = env('JWT_SIGNING_KEY', default=SECRET_KEY)
JWT_ALGORITHM = env('JWT_ALGORITHM', default='HS256')

# Secreto compartido para llamadas entre servicios.
INTERNAL_SERVICE_SECRET = env('INTERNAL_SERVICE_SECRET', default='super_secret_token')

# `ServiceHelper.call(service_name='IAM')` lee SERVICE_IAM_URL.
SERVICE_IAM_URL = env('SERVICE_IAM_URL', default='http://iam-service:8000')

# Comodidad de desarrollo: si el Host no resuelve a ninguna institución, se usa
# esta. Dejar vacío en producción — ahí el Host siempre debe resolver.
DEFAULT_TENANT_SCHEMA = env('DEFAULT_TENANT_SCHEMA', default='')

# Atajo de desarrollo: autentica cualquier petición como un usuario ficticio
# mientras no exista pantalla de acceso. Ignorado si DEBUG=False.
# APAGARLO en cuanto haya login.
DEV_AUTH_BYPASS = env.bool('DEV_AUTH_BYPASS', default=False)

CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_HEADERS = [
    'accept', 'authorization', 'content-type', 'origin',
    'x-internal-secret', 'x-tenant-schema',
]

# ──────────────────────────────────────────────────────────

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = env('TIME_ZONE', default='America/Guayaquil')
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': env('LOG_LEVEL', default='INFO')},
}
