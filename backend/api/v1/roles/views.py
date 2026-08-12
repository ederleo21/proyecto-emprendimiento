"""Gestión de roles y sus permisos.

Los **permisos** se declaran en `permissions.py` y no se crean desde acá: uno
existe porque hay código que lo comprueba. Lo que se gestiona son los
**roles** —combinaciones de esos permisos— que son decisiones de la
organización y cambian sin desplegar.

Hay dos protecciones que no son opcionales, porque el daño que evitan solo se
arregla entrando a la base de datos:

  1. No se puede quitar el último permiso de gestión de roles que queda en pie.
     Sin eso, nadie podría volver a repartir permisos nunca.
  2. No se puede borrar un rol que tiene gente asignada, ni uno del sistema.
"""
from django.db.models import Count, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from accounts.models import Role, RolePermission
from accounts.serializers import RoleDetailSerializer, RoleSerializer
from core.my_response import MyResponse
from core.permissions import HasOutreachPermission
from permissions import ALL_CODES, MODULE_ORDER, by_module

# El permiso que abre esta misma pantalla. Es el que no se puede perder.
MANAGE_ROLES = 'OUTREACH_ROLE_EDIT'


def _with_counts(qs):
    """Agrega cuánta gente y cuántos permisos tiene cada rol."""
    return qs.annotate(
        people=Count('memberships', distinct=True),
        permission_count=Count('permissions', distinct=True),
    )


class PermissionCatalogView(APIView):
    """`GET /roles/permissions/` — el catálogo, agrupado por módulo.

    Es lo que dibuja la matriz: una fila por módulo con sus casillas. Sale del
    código, así que no hay nada que guardar ni que editar.
    """

    permission_classes = [IsAuthenticated, HasOutreachPermission]
    required_permissions = {'GET': 'OUTREACH_ROLE_VIEW'}

    def get(self, request):
        grouped = by_module()
        return MyResponse.success(
            data=[
                {'module': module, 'permissions': grouped.get(module, [])}
                for module in MODULE_ORDER
            ],
            message='Catálogo de permisos.',
        )


class RoleListCreateView(APIView):
    """`GET /roles/` · `POST /roles/`"""

    permission_classes = [IsAuthenticated, HasOutreachPermission]
    required_permissions = {
        'GET': 'OUTREACH_ROLE_VIEW',
        'POST': MANAGE_ROLES,
    }

    def get(self, request):
        rows = _with_counts(Role.objects.all())
        return MyResponse.success(
            data=RoleSerializer(rows, many=True).data,
            message='Roles listados.',
        )

    def post(self, request):
        ser = RoleSerializer(data=request.data)
        if not ser.is_valid():
            return MyResponse.error(message='Datos inválidos.', errors=ser.errors)

        name = ser.validated_data['name'].strip()
        code = _code_for(name)
        if Role.objects.filter(code=code).exists():
            return MyResponse.error(
                message='Ya existe un rol con ese nombre.',
                errors={'name': ['Ya existe un rol con ese nombre.']},
                status_code=400,
            )

        role = ser.save(code=code)

        # Clonar de otro rol existente, como el "Clonar perfil" de cualquier
        # gestor de permisos: casi siempre uno nuevo se parece a uno que ya hay.
        clone_from = request.data.get('clone_from')
        if clone_from:
            origen = Role.objects.filter(pk=clone_from).first()
            if origen:
                RolePermission.objects.bulk_create(
                    [RolePermission(role=role, code=c) for c in origen.permission_codes],
                    ignore_conflicts=True,
                )

        role = _with_counts(Role.objects.filter(pk=role.pk)).first()
        return MyResponse.success(
            data=RoleDetailSerializer(role).data,
            message='Rol creado.',
            status_code=201,
        )


def _code_for(name: str) -> str:
    """Un código a partir del nombre: mayúsculas y guiones bajos."""
    import re
    import unicodedata

    plano = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Z0-9]+', '_', plano.upper()).strip('_')[:60] or 'ROL'


class RoleDetailView(APIView):
    """`GET`/`PATCH`/`DELETE /roles/<id>/`"""

    permission_classes = [IsAuthenticated, HasOutreachPermission]
    required_permissions = {
        'GET': 'OUTREACH_ROLE_VIEW',
        'PATCH': MANAGE_ROLES,
        'DELETE': MANAGE_ROLES,
    }

    def _get(self, pk):
        return _with_counts(Role.objects.filter(pk=pk)).first()

    def get(self, request, pk):
        role = self._get(pk)
        if role is None:
            return MyResponse.error(message='Rol no encontrado.', status_code=404)
        return MyResponse.success(data=RoleDetailSerializer(role).data)

    def patch(self, request, pk):
        """Cambia el nombre, la descripción o los permisos del rol."""
        role = self._get(pk)
        if role is None:
            return MyResponse.error(message='Rol no encontrado.', status_code=404)

        # ── Los permisos, si vienen ──────────────────────────────────
        if 'permissions' in request.data:
            pedidos = request.data.get('permissions')
            if not isinstance(pedidos, list):
                return MyResponse.error(
                    message='Datos inválidos.',
                    errors={'permissions': ['Debe ser una lista de códigos.']},
                    status_code=400,
                )

            desconocidos = [c for c in pedidos if c not in ALL_CODES]
            if desconocidos:
                return MyResponse.error(
                    message='Hay permisos que no existen.',
                    errors={'permissions': [
                        f'No están en el catálogo: {", ".join(sorted(desconocidos))}.'
                    ]},
                    status_code=400,
                )

            bloqueo = _would_lock_everyone_out(role, set(pedidos))
            if bloqueo:
                return MyResponse.error(message=bloqueo, status_code=409)

            role.permissions.exclude(code__in=pedidos).delete()
            RolePermission.objects.bulk_create(
                [RolePermission(role=role, code=c) for c in pedidos],
                ignore_conflicts=True,
            )

        # ── El nombre y lo demás ─────────────────────────────────────
        ser = RoleSerializer(role, data=request.data, partial=True)
        if not ser.is_valid():
            return MyResponse.error(message='Datos inválidos.', errors=ser.errors)
        ser.save()

        return MyResponse.success(
            data=RoleDetailSerializer(self._get(pk)).data,
            message='Rol actualizado.',
        )

    def delete(self, request, pk):
        role = self._get(pk)
        if role is None:
            return MyResponse.error(message='Rol no encontrado.', status_code=404)

        if role.is_system:
            return MyResponse.error(
                message=(
                    f'"{role.name}" viene con el sistema y no se puede eliminar. '
                    f'Si no se usa, se puede desactivar.'
                ),
                status_code=409,
            )

        if role.people:
            return MyResponse.error(
                message=(
                    f'"{role.name}" está asignado a {role.people} persona(s). '
                    f'Hay que moverlas a otro rol antes de eliminarlo.'
                ),
                status_code=409,
            )

        bloqueo = _would_lock_everyone_out(role, set())
        if bloqueo:
            return MyResponse.error(message=bloqueo, status_code=409)

        role.delete()
        return MyResponse.success(message='Rol eliminado.')


def _would_lock_everyone_out(role, permisos_nuevos: set) -> str | None:
    """Motivo por el que el cambio dejaría a la institución sin quien reparta
    permisos, o `None` si no hay problema.

    Solo importa cuando el rol **tenía** el permiso de gestión y va a perderlo:
    si es el último que lo sostiene, después nadie podría devolvérselo a nadie
    y habría que entrar a la base de datos.
    """
    if MANAGE_ROLES not in role.permission_codes:
        return None
    if MANAGE_ROLES in permisos_nuevos:
        return None

    otros = (
        Role.objects
        .filter(is_active=True, permissions__code=MANAGE_ROLES)
        .exclude(pk=role.pk)
        .exists()
    )
    if otros:
        return None

    return (
        f'"{role.name}" es el único rol que puede gestionar permisos. '
        f'Si se le quita, nadie podría volver a repartirlos. '
        f'Primero dale ese permiso a otro rol.'
    )
