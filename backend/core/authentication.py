"""Autenticación sin tabla de usuarios.

Espejo de `core_shared.authentication`. Este servicio **no tiene login propio**:
valida el JWT que emite el IAM de InnoTech usando la misma clave de firma, y
arma un usuario en memoria que vive solo durante el request.

Dos modos:
  1. `X-Internal-Secret` — llamada entre servicios.
  2. `Bearer <jwt>` — usuario final autenticado en IAM.
"""
import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTUser:
    """Identidad extraída del JWT. No se guarda en ninguna tabla."""

    def __init__(self, payload: dict):
        # IAM usa SimpleJWT (`user_id`); los otros claims van de respaldo.
        self.id = payload.get('user_id') or payload.get('sub') or payload.get('id')
        self.username = payload.get('username', '')
        self.email = payload.get('email', '')
        self.full_name = payload.get('full_name', '') or ''

        self.tenant_id = payload.get('tenant_id')
        if not self.tenant_id:
            active_tenant = payload.get('active_tenant') or {}
            if isinstance(active_tenant, dict):
                self.tenant_id = active_tenant.get('id')

        self.is_authenticated = True
        self.is_active = True
        self.is_staff = payload.get('is_staff', False)
        self.is_superuser = payload.get('is_superuser', False)

        self._payload = payload
        self._permissions = frozenset(payload.get('permissions') or [])
        self._denied_permissions = frozenset(payload.get('denied_permissions') or [])

    @property
    def active_role(self):
        return (self._payload or {}).get('active_role')

    @property
    def pk(self):
        return self.id

    def has_iam_permission(self, code: str) -> bool:
        """Permisos federados del tenant activo (claim `permissions` del JWT)."""
        if not code:
            return self.is_authenticated
        if self.is_superuser:
            return True
        if code in self._denied_permissions:
            return False
        return code in self._permissions

    def __str__(self):
        return self.username or str(self.id)


class InternalServiceUser:
    """Usuario virtual para llamadas entre servicios. Satisface `IsAuthenticated`."""

    id = None
    username = 'internal-service'
    email = ''
    tenant_id = None
    is_authenticated = True
    is_active = True
    is_staff = False
    is_superuser = False
    _payload: dict = {}

    @property
    def pk(self):
        return self.id

    def has_iam_permission(self, code: str) -> bool:
        # Una llamada entre servicios ya pasó el filtro del secreto compartido.
        return True

    def __str__(self):
        return self.username


class DevUser(JWTUser):
    """Usuario ficticio para desarrollar sin login.

    Existe **solo** mientras el servicio no tenga pantalla de acceso. Se activa
    con `DEV_AUTH_BYPASS=True` en el `.env` y el arranque avisa en el log.
    """

    def __init__(self):
        super().__init__({
            'username': 'dev',
            'email': 'dev@localhost',
            'is_superuser': True,
            'full_name': 'Usuario de desarrollo',
        })


class DevAuthentication(BaseAuthentication):
    """Autentica a cualquiera como `DevUser` si `DEV_AUTH_BYPASS` está activo.

    Se declara **después** de `ServiceJWTAuthentication` en los settings, así
    que un JWT real o el secreto entre servicios siguen mandando; esto solo
    actúa cuando no llegó ninguna credencial.

    Con `DEBUG=False` no hace nada, aunque el flag esté encendido: es la última
    barrera para que no se cuele a producción por un `.env` mal copiado.
    """

    def authenticate(self, request):
        if not getattr(settings, 'DEV_AUTH_BYPASS', False):
            return None
        if not getattr(settings, 'DEBUG', False):
            return None
        return (DevUser(), None)


class ServiceJWTAuthentication(BaseAuthentication):
    """Devuelve `None` si no hay credenciales — DRF se encarga del 401."""

    def authenticate(self, request):
        internal_secret = request.META.get('HTTP_X_INTERNAL_SECRET', '')
        expected_secret = getattr(settings, 'INTERNAL_SERVICE_SECRET', None)
        if internal_secret and expected_secret and internal_secret == expected_secret:
            return (InternalServiceUser(), None)

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # Respaldo para conexiones que el navegador abre sin headers
            # propios (EventSource, WebSocket).
            token = request.GET.get('token', '')
            if not token:
                return None

        try:
            payload = jwt.decode(
                token,
                getattr(settings, 'JWT_SIGNING_KEY', settings.SECRET_KEY),
                algorithms=[getattr(settings, 'JWT_ALGORITHM', 'HS256')],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expirado.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token inválido.')

        return (JWTUser(payload), token)

    def authenticate_header(self, request):
        return 'Bearer'
