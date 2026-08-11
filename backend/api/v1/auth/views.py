"""Acceso al sistema.

Rutas alineadas con las del IAM de InnoTech (`/auth/sign-in/`, `/auth/refresh/`)
para que el frontend no tenga que cambiar de forma el día de la integración.
"""
import jwt
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.models import User
from accounts.tokens import decode_refresh, issue_tokens
from core.my_response import MyResponse


class SignInView(APIView):
    """`POST /auth/sign-in/` — usuario y contraseña a cambio de un JWT."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''

        if not username or not password:
            return MyResponse.error(
                message='Usuario y contraseña son obligatorios.',
                errors={'username': ['Requerido.'], 'password': ['Requerido.']},
                status_code=400,
            )

        user = User.objects.filter(username__iexact=username).first()

        # Mismo mensaje si el usuario no existe o si la contraseña está mal:
        # decir cuál de las dos falló le regala información a quien pruebe
        # usuarios al azar.
        if user is None or not user.check_password(password):
            return MyResponse.error(
                message='Usuario o contraseña incorrectos.', status_code=401,
            )

        if not user.is_active:
            return MyResponse.error(
                message='La cuenta está desactivada.', status_code=403,
            )

        tokens = issue_tokens(user)
        return MyResponse.success(
            data={
                **tokens,
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_superuser': user.is_superuser,
                },
            },
            message='Acceso concedido.',
        )


class RefreshView(APIView):
    """`POST /auth/refresh/` — un `access` nuevo a partir del `refresh`."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('refresh') or ''
        if not token:
            return MyResponse.error(message='Falta el token de refresco.', status_code=400)

        try:
            payload = decode_refresh(token)
        except jwt.ExpiredSignatureError:
            return MyResponse.error(message='El token de refresco expiró.', status_code=401)
        except jwt.InvalidTokenError:
            return MyResponse.error(message='Token de refresco inválido.', status_code=401)

        user = User.objects.filter(id=payload.get('user_id'), is_active=True).first()
        if user is None:
            return MyResponse.error(message='La cuenta ya no está disponible.', status_code=401)

        return MyResponse.success(data=issue_tokens(user), message='Token renovado.')
