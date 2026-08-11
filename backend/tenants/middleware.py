"""Resolución del tenant, tolerante a fallos.

`django-tenants` resuelve por el `Host`. Eso rompe en dos casos reales:

  - En desarrollo el navegador manda `localhost`, no `itb.localhost`.
  - Las llamadas entre servicios no tienen host de tenant.

Este middleware añade dos salidas antes de rendirse:

  1. Cabecera `X-Tenant-Schema` — la que usan las llamadas entre servicios.
  2. `DEFAULT_TENANT_SCHEMA` del `.env` — comodidad de desarrollo, para no
     tener que tocar el archivo `hosts` de Windows.

Si nada resuelve, se sirve el schema `public`, donde solo viven las tablas
compartidas: una petición sin tenant no ve datos de ninguna institución.
"""
import logging

from django.conf import settings
from django.db import connection
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_public_schema_name, get_tenant_model

logger = logging.getLogger(__name__)


class RobustTenantMiddleware(TenantMainMiddleware):

    def process_request(self, request):
        TenantModel = get_tenant_model()

        # 1. Cabecera explícita: gana sobre todo lo demás.
        schema_name = (request.META.get('HTTP_X_TENANT_SCHEMA') or '').strip()
        if schema_name:
            tenant = TenantModel.objects.filter(schema_name=schema_name).first()
            if tenant:
                return self._activate(request, tenant)
            logger.warning('X-Tenant-Schema="%s" no corresponde a ningún tenant', schema_name)

        # 2. El camino normal de django-tenants: por Host.
        try:
            return super().process_request(request)
        except Exception:
            logger.debug('No se pudo resolver el tenant por Host; probando el de por defecto')

        # 3. Respaldo de desarrollo.
        fallback = getattr(settings, 'DEFAULT_TENANT_SCHEMA', '')
        if fallback:
            tenant = TenantModel.objects.filter(schema_name=fallback).first()
            if tenant:
                return self._activate(request, tenant)

        # 4. Sin tenant: schema público, sin datos de institución.
        connection.set_schema_to_public()
        request.tenant = None

    def _activate(self, request, tenant):
        request.tenant = tenant
        connection.set_tenant(tenant)
        return None

    @staticmethod
    def is_public(request) -> bool:
        return getattr(request, 'tenant', None) is None or (
            request.tenant.schema_name == get_public_schema_name()
        )
