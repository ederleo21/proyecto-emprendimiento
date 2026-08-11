"""Vistas transversales de la API."""
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.my_response import MyResponse


class HealthCheckView(APIView):
    """`GET /api/v1/health/` — sirve para el healthcheck de Docker.

    Abierto a propósito: si exigiera token, un contenedor sin IAM se marcaría
    como caído aunque esté sano.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        tenant = getattr(request, 'tenant', None)
        return MyResponse.success(
            data={
                'status': 'healthy',
                'service': 'outreach',
                # Útil para depurar la resolución de institución: si esto sale
                # nulo, el Host no resolvió y se está en el schema público.
                'tenant': tenant.schema_name if tenant else None,
            },
            message='Outreach Service is running',
        )


class WhoAmIView(APIView):
    """`GET /api/v1/whoami/` — devuelve lo que el JWT trae del usuario.

    Existe para comprobar la integración con IAM sin tener aún pantallas:
    si esto responde, la firma del token y el tenant están bien configurados.
    """

    def get(self, request):
        user = request.user
        tenant = getattr(request, 'tenant', None)
        return MyResponse.success(data={
            'id': str(user.id) if getattr(user, 'id', None) else None,
            'username': getattr(user, 'username', ''),
            'email': getattr(user, 'email', ''),
            'is_superuser': getattr(user, 'is_superuser', False),
            'tenant': tenant.schema_name if tenant else None,
        })
