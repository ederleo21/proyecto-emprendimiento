"""Llamadas HTTP a otros microservicios.

Espejo de `core_shared.helpers.service_helper`.

Regla de la arquitectura: **ningún servicio consulta la base de datos de otro**.
Los datos ajenos se piden por aquí y se guardan en tablas réplica locales.

La URL sale de `settings.SERVICE_<NOMBRE>_URL`, así que
`ServiceHelper.call(service_name='IAM', ...)` busca `SERVICE_IAM_URL`.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ServiceCallError(Exception):
    """El otro servicio respondió con un error."""

    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f'HTTP {status_code}: {detail}')


class ServiceHelper:

    @staticmethod
    def authorization_from_request(request) -> dict:
        """Reenvía el Bearer del request entrante.

        Hace falta con endpoints que exigen un usuario real: el secreto entre
        servicios no sirve si el otro lado solo acepta JWT.
        """
        if not request:
            return {}
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        return {'Authorization': auth} if auth else {}

    @staticmethod
    def call(
        service_name,
        endpoint,
        method='GET',
        data=None,
        params=None,
        headers=None,
        files=None,
        request=None,
        raw=False,
        timeout=30,
    ):
        base_url = getattr(settings, f'SERVICE_{service_name.upper()}_URL')
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        request_headers = {'X-Internal-Secret': settings.INTERNAL_SERVICE_SECRET}
        if not files:
            request_headers['Content-Type'] = 'application/json'
        if headers:
            request_headers.update(headers)
        if request and 'Authorization' not in request_headers:
            request_headers.update(ServiceHelper.authorization_from_request(request))

        request_kwargs = {
            'method': method,
            'url': url,
            'params': params,
            'headers': request_headers,
            # Nunca sin timeout: un servicio caído no debe colgar el request
            # entrante hasta que el gateway corte con 504.
            'timeout': timeout,
        }
        if files:
            request_kwargs['data'] = data or {}
            request_kwargs['files'] = files
        else:
            request_kwargs['json'] = data

        response = requests.request(**request_kwargs)

        if not response.ok:
            try:
                error_body = response.json()
            except Exception:
                error_body = {'detail': response.text[:500] or f'HTTP {response.status_code}'}
            raise ServiceCallError(status_code=response.status_code, detail=error_body)

        if raw:
            return response.content

        try:
            return response.json()
        except Exception:
            logger.warning('ServiceHelper: la respuesta de %s no era JSON válido', url)
            return {}
