"""Identidad visual de la institución.

El color de marca **no se escribe en el código**: cada institución configura el
suyo y el frontend lo aplica en runtime sobre los tokens del design system.
Mismo criterio que el branding del monorepo de InnoTech.

Abierto sin token a propósito: el frontend necesita los colores y el nombre
**antes** de que el usuario inicie sesión, para que la pantalla de acceso ya
salga con la identidad correcta.
"""
import re

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from core.my_response import MyResponse
from core.permissions import HasOutreachPermission
from tenants.models import COLOR_POR_DEFECTO, COLOR_SECUNDARIO_POR_DEFECTO

# Se usa cuando no hay institución resuelta o no configuró nada. No es la
# identidad de nadie: es un neutro para que la pantalla no salga rota.
DEFAULT_BRANDING = {
    'name': 'Vinculación con la Sociedad',
    'subtitle': '',
    'primary_color': COLOR_POR_DEFECTO,
    'secondary_color': COLOR_SECUNDARIO_POR_DEFECTO,
    'logo_url': None,
}

# `#RGB` o `#RRGGBB`. Se valida acá y no solo en la pantalla: el color entra
# como texto en un `style` del navegador, así que lo que se guarde tiene que
# ser un color y no cualquier cadena.
HEX_COLOR = re.compile(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')

EDITABLE_COLORS = ('primary_color', 'secondary_color')

# El nombre lo manda el IAM cuando está conectado —`sync_tenants` lo
# sobreescribe—, pero mientras no lo esté hay que poder corregirlo: si no, un
# nombre mal escrito al crear la institución queda congelado.
EDITABLE_TEXTS = ('name', 'subtitle')

MAX_TEXT_LENGTH = {'name': 255, 'subtitle': 120}


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
            data=_branding_of(tenant, request),
            message='Branding de la institución.',
        )


def _branding_of(tenant, request) -> dict:
    """La identidad vive en el modelo `Tenant`, alineado con el branding del
    IAM. Si algún campo quedó vacío se cae al neutro.

    `logo_url` se manda **absoluta**. Quien la consume corre en otro puerto
    —o en otro origin, embebido en el shell—, así que una ruta relativa la
    buscaría en su propio servidor y saldría la imagen rota.

    Por eso `request` es obligatorio y no opcional: cuando podía omitirse, se
    omitió, y el logo no cargaba.
    """
    logo_url = request.build_absolute_uri(tenant.logo.url) if tenant.logo else None

    return {
        'name': tenant.name or DEFAULT_BRANDING['name'],
        'subtitle': tenant.subtitle,
        'primary_color': tenant.primary_color or DEFAULT_BRANDING['primary_color'],
        'secondary_color': tenant.secondary_color or DEFAULT_BRANDING['secondary_color'],
        'logo_url': logo_url,
        'tenant': tenant.schema_name,
    }


class BrandingAdminView(APIView):
    """`GET`/`PATCH /api/v1/branding/settings/` — la identidad, editable.

    Separada de `BrandingView` a propósito, siguiendo al IAM: aquella es
    pública porque la pantalla de acceso necesita los colores antes de que
    nadie inicie sesión; esta exige administrador porque cambia lo que ve toda
    la institución.
    """

    permission_classes = [IsAuthenticated, HasOutreachPermission]
    required_permissions = {
        'GET': 'OUTREACH_SETTINGS_VIEW',
        'PATCH': 'OUTREACH_BRANDING_EDIT',
    }

    def get(self, request):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return MyResponse.error(
                message='No hay institución resuelta en este request.',
                status_code=400,
            )
        return MyResponse.success(
            data=_branding_of(tenant, request),
            message='Branding de la institución.',
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

        for field in EDITABLE_TEXTS:
            if field not in request.data:
                continue
            value = (request.data.get(field) or '').strip()
            if field == 'name' and not value:
                errors[field] = ['El nombre de la institución no puede quedar vacío.']
                continue
            if len(value) > MAX_TEXT_LENGTH[field]:
                errors[field] = [
                    f'No puede pasar de {MAX_TEXT_LENGTH[field]} caracteres.'
                ]
                continue
            setattr(tenant, field, value)
            changed.append(field)

        if errors:
            return MyResponse.error(
                message='Datos inválidos.', errors=errors, status_code=400,
            )
        if not changed:
            return MyResponse.error(
                message='No se envió ningún campo para actualizar.',
                errors={'primary_color': ['Requerido si no se envía otro campo.']},
                status_code=400,
            )

        # `update_fields` y no un `save()` pelado: el schema del tenant se
        # crea al guardar y no hay por qué tocarlo para cambiar un color.
        tenant.save(update_fields=changed)

        return MyResponse.success(
            data=_branding_of(tenant, request),
            message='Identidad visual actualizada.',
        )


class BrandingLogoView(APIView):
    """`POST`/`DELETE /api/v1/branding/settings/logo/` — el logotipo.

    Va aparte del `PATCH` de los otros campos porque un archivo viaja como
    `multipart` y el resto como JSON: mezclarlos obligaría a mandar todo en
    `multipart` aunque no haya archivo.
    """

    permission_classes = [IsAuthenticated, HasOutreachPermission]
    required_permissions = {
        'POST': 'OUTREACH_BRANDING_EDIT',
        'DELETE': 'OUTREACH_BRANDING_EDIT',
    }
    parser_classes = [MultiPartParser, FormParser]

    def _tenant_or_error(self, request):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return None, MyResponse.error(
                message='No hay institución resuelta en este request.',
                status_code=400,
            )
        return tenant, None

    def post(self, request):
        tenant, error = self._tenant_or_error(request)
        if error:
            return error

        archivo = request.FILES.get('logo')
        if archivo is None:
            return MyResponse.error(
                message='No llegó ningún archivo.',
                errors={'logo': ['Requerido.']},
                status_code=400,
            )

        # Se asigna y se valida con el modelo, para no repetir acá las reglas
        # de extensión y peso que ya declara el campo.
        tenant.logo = archivo
        try:
            tenant.full_clean(exclude=[f.name for f in tenant._meta.fields if f.name != 'logo'])
        except DjangoValidationError as e:
            return MyResponse.error(
                message='El archivo no sirve como logotipo.',
                errors={'logo': e.message_dict.get('logo', [str(e)])},
                status_code=400,
            )

        tenant.save(update_fields=['logo'])
        return MyResponse.success(
            data=_branding_of(tenant, request), message='Logotipo actualizado.',
        )

    def delete(self, request):
        tenant, error = self._tenant_or_error(request)
        if error:
            return error

        if tenant.logo:
            # `save=False` y luego un save explícito: así el borrado del
            # archivo y el vaciado del campo van juntos.
            tenant.logo.delete(save=False)
            tenant.logo = None
            tenant.save(update_fields=['logo'])

        return MyResponse.success(
            data=_branding_of(tenant, request), message='Logotipo quitado.',
        )
