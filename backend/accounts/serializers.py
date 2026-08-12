"""Serializers de roles y permisos."""
from rest_framework import serializers

from accounts.models import Role
from permissions import ALL_CODES


class RoleSerializer(serializers.ModelSerializer):
    """Un rol tal como lo muestra el listado.

    `people` y `permission_count` van calculados para que la lista se pinte sin
    una consulta por fila.
    """

    people = serializers.IntegerField(read_only=True)
    permission_count = serializers.IntegerField(read_only=True)
    scope_label = serializers.CharField(source='get_scope_display', read_only=True)

    class Meta:
        model = Role
        fields = [
            'id', 'code', 'name', 'description', 'scope', 'scope_label',
            'is_system', 'is_active', 'people', 'permission_count',
        ]
        # El código identifica al rol en asignaciones y en el token: cambiarlo
        # dejaría huérfano lo que ya lo referencia.
        read_only_fields = ['id', 'code', 'is_system']
        extra_kwargs = {
            'name': {
                'error_messages': {
                    'blank': 'El nombre del rol es obligatorio.',
                    'required': 'El nombre del rol es obligatorio.',
                },
            },
        }


class RoleDetailSerializer(RoleSerializer):
    """El rol con la lista de permisos que tiene concedidos."""

    permissions = serializers.SerializerMethodField()

    class Meta(RoleSerializer.Meta):
        fields = RoleSerializer.Meta.fields + ['permissions']

    def get_permissions(self, obj) -> list:
        # Solo los que siguen existiendo en el catálogo: si se retiró una
        # funcionalidad, su permiso quedó huérfano y no debe aparecer.
        return sorted(obj.permission_codes & ALL_CODES)
