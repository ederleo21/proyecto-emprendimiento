"""Emisión de tokens.

La clave del diseño: **los claims son los mismos que emite el IAM de InnoTech**
(ver `core/authentication.py`, que es quien los lee). Así el validador no
distingue un token nuestro de uno suyo, y el día de la integración se cambia la
clave de firma y se borra este módulo.

Se emiten dos tokens, como SimpleJWT:
  - `access`  — corto, viaja en cada petición.
  - `refresh` — largo, solo sirve para pedir un `access` nuevo.
"""
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings

ACCESS_MINUTES = 60 * 8      # una jornada de trabajo
REFRESH_DAYS = 7


def _sign(payload: dict) -> str:
    return jwt.encode(
        payload,
        getattr(settings, 'JWT_SIGNING_KEY', settings.SECRET_KEY),
        algorithm=getattr(settings, 'JWT_ALGORITHM', 'HS256'),
    )


def _base_claims(user, tenant=None) -> dict:
    """Claims compatibles con los que emite el IAM."""
    memberships = [
        {
            'tenant_id': str(m.tenant_id),
            'tenant_name': m.tenant.name,
            'tenant_slug': m.tenant.schema_name,
            'role_name': m.role,
        }
        for m in user.memberships.select_related('tenant').all()
    ]

    # Si no se indicó institución se toma la primera: con una sola membresía
    # —el caso normal— no tiene sentido preguntar.
    active = tenant
    if active is None and memberships:
        active = user.memberships.select_related('tenant').first().tenant

    return {
        # IAM usa `user_id` (SimpleJWT). Los demás claims van igual que allá.
        'user_id': str(user.id),
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        # Todavía no hay catálogo de permisos en este servicio. Se manda la
        # lista vacía para que el claim exista y `has_iam_permission` funcione
        # sin ramas especiales; un superusuario pasa igual.
        'permissions': [],
        'denied_permissions': [],
        'memberships': memberships,
        'tenant_id': str(active.id) if active else None,
        'active_tenant': (
            {'id': str(active.id), 'name': active.name, 'slug': active.schema_name}
            if active else None
        ),
    }


def issue_tokens(user, tenant=None) -> dict:
    """Devuelve `{access, refresh}` para el usuario."""
    now = datetime.now(timezone.utc)
    claims = _base_claims(user, tenant)

    access = _sign({
        **claims,
        'token_type': 'access',
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=ACCESS_MINUTES)).timestamp()),
    })
    refresh = _sign({
        'user_id': str(user.id),
        'token_type': 'refresh',
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(days=REFRESH_DAYS)).timestamp()),
    })
    return {'access': access, 'refresh': refresh}


def decode_refresh(token: str) -> dict:
    """Valida un refresh y devuelve sus claims. Lanza `jwt.InvalidTokenError`."""
    payload = jwt.decode(
        token,
        getattr(settings, 'JWT_SIGNING_KEY', settings.SECRET_KEY),
        algorithms=[getattr(settings, 'JWT_ALGORITHM', 'HS256')],
    )
    if payload.get('token_type') != 'refresh':
        raise jwt.InvalidTokenError('El token no es de refresco.')
    return payload
