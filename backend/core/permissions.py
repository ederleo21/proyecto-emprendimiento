"""Comprobación de permisos en las vistas.

Espejo de `HasPeriodsPermission` y compañía en `academic_service`: una clase de
permiso de DRF que lee el código exigido por la vista y lo busca en el token.

El permiso viaja **dentro del token**, resuelto al iniciar sesión. Por eso
comprobarlo no cuesta una consulta: es mirar una lista que ya está en memoria.

Uso:

    class ProjectListCreateView(APIView):
        permission_classes = [IsAuthenticated, HasOutreachPermission]
        required_permissions = {
            'GET': 'OUTREACH_PROJECT_VIEW',
            'POST': 'OUTREACH_PROJECT_CREATE',
        }
"""
from rest_framework.permissions import BasePermission


class HasOutreachPermission(BasePermission):
    """Exige el permiso que la vista declare para el método de la petición.

    Una vista sin `required_permissions` no exige nada: hay endpoints que solo
    piden estar autenticado —el de salud, el branding público— y obligarlos a
    declarar un permiso vacío sería ruido.
    """

    message = 'No tiene permiso para realizar esta acción.'

    def has_permission(self, request, view):
        required = getattr(view, 'required_permissions', None)
        if not required:
            return True

        code = required.get(request.method)
        if not code:
            return True

        user = getattr(request, 'user', None)
        if user is None or not getattr(user, 'is_authenticated', False):
            return False

        # `has_iam_permission` lo trae tanto el usuario del JWT como el de las
        # llamadas entre servicios, que responde que sí a todo — ya pasó el
        # filtro del secreto compartido.
        comprobar = getattr(user, 'has_iam_permission', None)
        if comprobar is None:
            # Un usuario sin ese método no viene de este sistema de tokens.
            # Se deja pasar solo si es superusuario, para no romper el acceso
            # de emergencia.
            return bool(getattr(user, 'is_superuser', False))

        return comprobar(code)
