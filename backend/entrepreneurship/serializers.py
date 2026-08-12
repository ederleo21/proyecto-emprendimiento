"""Serializers del Proyecto de Emprendimiento."""
from django.utils import timezone
from rest_framework import serializers

from .models import Configuration, Project, ProjectActivity, Stage, StageActivity


def next_project_code() -> str:
    """Siguiente código libre, con el formato que configuró la institución.

    El prefijo, el año y los dígitos salen de `Configuration`, no de constantes:
    una institución puede querer `EMP-0001` y otra `PE-2026-001`.

    Se busca contra `all_objects` —el manager que ve también lo archivado— y no
    contra `objects`. La constraint de unicidad solo mira las filas vivas, así
    que técnicamente se podría reusar el código de un proyecto archivado; pero
    un código lo lee una persona y termina en actas, así que reciclarlo sería
    confuso. Una vez usado, no vuelve.
    """
    config = Configuration.load()
    year = timezone.now().year
    prefix = config.code_prefix(year)

    used = set(
        Project.all_objects
        .filter(code__startswith=prefix)
        .values_list('code', flat=True)
    )
    number = len(used) + 1
    while config.format_code(year, number) in used:
        number += 1
    return config.format_code(year, number)


class ConfigurationSerializer(serializers.ModelSerializer):
    """Parámetros del módulo para esta institución.

    `code_example` no es un campo guardado: es cómo quedaría el próximo código
    con lo que hay puesto. Va en la respuesta porque la pantalla necesita
    mostrar el efecto de cada cambio, y armar el formato de nuevo del lado del
    navegador sería repetir la regla que ya vive acá.
    """

    code_example = serializers.SerializerMethodField()

    class Meta:
        model = Configuration
        fields = [
            'id',
            'project_code_prefix',
            'project_code_include_year',
            'project_code_digits',
            'code_example',
        ]
        read_only_fields = ['id']

    def get_code_example(self, obj) -> str:
        return obj.format_code(timezone.now().year, 1)


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
        # El código lo pone el sistema y no se edita: identifica al proyecto en
        # actas y conversaciones, así que cambiarlo rompería referencias que ya
        # están fuera de la aplicación.
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
        extra_kwargs = {
            'title': {
                'error_messages': {
                    'blank': 'El título del proyecto es obligatorio.',
                    'required': 'El título del proyecto es obligatorio.',
                },
            },
        }

    def create(self, validated_data):
        validated_data['code'] = next_project_code()
        return super().create(validated_data)


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
