"""Identidad visual de la institución.

El color de marca **no se escribe en el código**: cada institución configura el
suyo y el frontend lo aplica en runtime sobre los tokens del design system.
Mismo criterio que el branding del monorepo de InnoTech.

Abierto sin token a propósito: el frontend necesita los colores y el nombre
**antes** de que el usuario inicie sesión, para que la pantalla de acceso ya
salga con la identidad correcta.
"""
import re

from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

from core.my_response import MyResponse
from tenants.models import COLOR_POR_DEFECTO, COLOR_SECUNDARIO_POR_DEFECTO

# Se usa cuando no hay institución resuelta o no configuró nada. No es la
# identidad de nadie: es un neutro para que la pantalla no salga rota.
DEFAULT_BRANDING = {
    'name': 'Vinculación con la Sociedad',
    'primary_color': COLOR_POR_DEFECTO,
    'secondary_color': COLOR_SECUNDARIO_POR_DEFECTO,
}

# `#RGB` o `#RRGGBB`. Se valida acá y no solo en la pantalla: el color entra
# como texto en un `style` del navegador, así que lo que se guarde tiene que
# ser un color y no cualquier cadena.
HEX_COLOR = re.compile(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')

EDITABLE_COLORS = ('primary_color', 'secondary_color')


class BrandingView(APIView):
    """`GET /api/v1/branding/` — nombre y color de la institución activa."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return MyResponse.success(
                data={**DEFAULT_BRANDING, 'tenant': None},
                message='Branding por defecto (sin institución resuelta).',
            )

        return MyResponse.success(
            data=_branding_of(tenant),
            message='Branding de la institución.',
        )


def _branding_of(tenant) -> dict:
    """Los colores viven en el modelo `Tenant`, alineado con el branding del
    IAM. Si alguno quedó vacío se cae al neutro."""
    return {
        'name': tenant.name or DEFAULT_BRANDING['name'],
        'primary_color': tenant.primary_color or DEFAULT_BRANDING['primary_color'],
        'secondary_color': tenant.secondary_color or DEFAULT_BRANDING['secondary_color'],
        'tenant': tenant.schema_name,
    }


class BrandingAdminView(APIView):
    """`GET`/`PATCH /api/v1/branding/settings/` — la identidad, editable.

    Separada de `BrandingView` a propósito, siguiendo al IAM: aquella es
    pública porque la pantalla de acceso necesita los colores antes de que
    nadie inicie sesión; esta exige administrador porque cambia lo que ve toda
    la institución.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return MyResponse.error(
                message='No hay institución resuelta en este request.',
                status_code=400,
            )
        return MyResponse.success(
            data=_branding_of(tenant), message='Branding de la institución.',
        )

    def patch(self, request):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return MyResponse.error(
                message='No hay institución resuelta en este request.',
                status_code=400,
            )

        errors = {}
        changed = []
        for field in EDITABLE_COLORS:
            if field not in request.data:
                continue
            value = (request.data.get(field) or '').strip()
            if not HEX_COLOR.match(value):
                errors[field] = ['Debe ser un color en formato #RGB o #RRGGBB.']
                continue
            setattr(tenant, field, value.upper())
            changed.append(field)

        if errors:
            return MyResponse.error(
                message='Datos inválidos.', errors=errors, status_code=400,
            )
        if not changed:
            return MyResponse.error(
                message='No se envió ningún color para actualizar.',
                errors={'primary_color': ['Requerido si no se envía otro campo.']},
                status_code=400,
            )

        # `update_fields` y no un `save()` pelado: el schema del tenant se
        # crea al guardar y no hay por qué tocarlo para cambiar un color.
        tenant.save(update_fields=changed)

        return MyResponse.success(
            data=_branding_of(tenant), message='Identidad visual actualizada.',
        )
