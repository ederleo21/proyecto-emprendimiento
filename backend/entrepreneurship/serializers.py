"""Serializers del Proyecto de Emprendimiento."""
from rest_framework import serializers

from .models import Project, ProjectActivity, Stage, StageActivity


class StageActivitySerializer(serializers.ModelSerializer):
    """Actividad del catálogo, sin referencia a ningún proyecto."""

    class Meta:
        model = StageActivity
        fields = ['id', 'code', 'name', 'order', 'is_optional', 'is_derived']


class StageSerializer(serializers.ModelSerializer):
    """Etapa del proceso. Alimenta el filtro y las tarjetas de métricas."""

    class Meta:
        model = Stage
        fields = ['id', 'code', 'name', 'order', 'color']


class ProjectSerializer(serializers.ModelSerializer):
    """Proyecto tal como lo muestra el listado.

    `stage_name` y `stage_color` van denormalizados para que la tabla se pinte
    sin una consulta por fila. `progress` es calculado: sale de contar
    actividades confirmadas, no de un campo guardado.
    """

    stage_code = serializers.CharField(source='stage.code', read_only=True, default=None)
    stage_name = serializers.CharField(source='stage.name', read_only=True, default=None)
    stage_color = serializers.CharField(source='stage.color', read_only=True, default=None)
    progress = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'code', 'title',
            'stage', 'stage_code', 'stage_name', 'stage_color',
            'progress', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'title': {
                'error_messages': {
                    'blank': 'El título del proyecto es obligatorio.',
                    'required': 'El título del proyecto es obligatorio.',
                },
            },
        }


class ProjectStageSerializer(serializers.Serializer):
    """Una etapa vista desde un proyecto: sus actividades y su avance.

    No hay modelo detrás — se arma combinando el catálogo con lo que el
    proyecto tiene marcado. Por eso es `Serializer` y no `ModelSerializer`.
    """

    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()
    order = serializers.IntegerField()
    color = serializers.CharField()
    progress = serializers.IntegerField()
    activities = serializers.ListField()


class ProjectActivitySerializer(serializers.ModelSerializer):
    """Estado de una actividad dentro de un proyecto."""

    code = serializers.CharField(source='activity.code', read_only=True)
    name = serializers.CharField(source='activity.name', read_only=True)
    is_optional = serializers.BooleanField(source='activity.is_optional', read_only=True)

    class Meta:
        model = ProjectActivity
        fields = ['id', 'activity', 'code', 'name', 'is_optional',
                  'is_confirmed', 'confirmed_at']
        read_only_fields = ['id', 'confirmed_at']
