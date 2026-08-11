"""API del Proyecto de Emprendimiento.

Cubre el listado con sus filtros, el alta, y el detalle de un proyecto con sus
cinco etapas y el avance de cada una.

El avance sale de contar actividades confirmadas sobre aplicables — la regla
del mockup. Lo que NO está: quién puede confirmar una actividad, qué
entregable exige cada una, y si hay que cerrar una etapa para abrir la
siguiente. Eso no está definido y por eso no está inventado.
"""
from uuid import UUID

from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView

from core.my_response import MyResponse
from entrepreneurship.models import (
    Project, ProjectActivity, Stage, StageActivity,
)
from entrepreneurship.serializers import (
    ProjectSerializer, StageActivitySerializer, StageSerializer,
)


# Cuántos proyectos trae una página del listado. El tope no es capricho: sin
# él, `?page_size=` grande deja la paginación de adorno y devuelve la tabla
# entera.
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


def _create_fixed_activities(project):
    """Da de alta las actividades que aplican a todo proyecto.

    Las elegibles no se crean acá: aparecen cuando alguien las escoge.
    """
    fixed = StageActivity.objects.filter(is_active=True, is_optional=False)
    ProjectActivity.objects.bulk_create(
        [ProjectActivity(project=project, activity=a) for a in fixed],
        ignore_conflicts=True,
    )


class StageListView(APIView):
    """`GET /stages/` — las etapas del proceso, en orden."""

    def get(self, request):
        rows = Stage.objects.filter(is_active=True)
        return MyResponse.success(
            data=StageSerializer(rows, many=True).data,
            message='Etapas listadas.',
        )


class ProjectListCreateView(APIView):
    """`GET /projects/` con filtros · `POST /projects/` para el alta."""

    def get_queryset(self):
        qs = Project.objects.select_related('stage').prefetch_related(
            'activities__activity',
        )

        stage = (self.request.query_params.get('stage') or '').strip()
        if stage:
            # Se acepta el id o el código. La pantalla manda el código, que es
            # legible en la URL; un servicio podría mandar el id.
            try:
                qs = qs.filter(stage_id=UUID(stage))
            except (ValueError, AttributeError, TypeError):
                qs = qs.filter(stage__code=stage.upper())

        search = (self.request.query_params.get('search') or '').strip()
        if search:
            qs = qs.filter(title__icontains=search)

        return qs

    def _page_size(self) -> int:
        """Tamaño de página pedido, acotado.

        El tope existe para que `?page_size=100000` no sea una forma de pedir
        la tabla entera y tumbar la pantalla.
        """
        raw = self.request.query_params.get('page_size')
        if not raw:
            return DEFAULT_PAGE_SIZE
        try:
            return max(1, min(int(raw), MAX_PAGE_SIZE))
        except (TypeError, ValueError):
            return DEFAULT_PAGE_SIZE

    def get(self, request):
        page_size = self._page_size()
        paginator = Paginator(self.get_queryset(), page_size)
        # `get_page` acota solo: una página fuera de rango o no numérica cae en
        # la primera o la última en vez de reventar.
        page = paginator.get_page(request.query_params.get('page'))

        rows = list(page.object_list)
        # El catálogo es el mismo para todos: se carga una vez y se les presta.
        # Sin esto, cada fila lo consulta por su cuenta al calcular su avance.
        Project.share_catalog(rows)

        return MyResponse.success(
            data={
                'results': ProjectSerializer(rows, many=True).data,
                # `count` es el total de la consulta, no lo que trae esta
                # página: es lo que la paginación necesita para saber cuántas
                # páginas hay.
                'count': paginator.count,
                'page': page.number,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            },
            message='Proyectos listados.',
        )

    def post(self, request):
        ser = ProjectSerializer(data=request.data)
        if not ser.is_valid():
            return MyResponse.error(message='Datos inválidos.', errors=ser.errors)

        with transaction.atomic():
            obj = ser.save()
            # Un proyecto nace con sus actividades fijas: sin ellas el avance
            # no tendría sobre qué calcularse y la pantalla saldría vacía.
            _create_fixed_activities(obj)

        return MyResponse.success(
            data=ProjectSerializer(obj).data,
            message='Proyecto creado.',
            status_code=201,
        )


class ProjectDetailView(APIView):
    """`GET /projects/<id>/` — el proyecto con sus etapas y su avance.

    Es lo que alimenta el tablero: cinco tarjetas, una por etapa, cada una con
    su porcentaje y sus actividades.
    """

    def get(self, request, pk):
        project = (
            Project.objects.select_related('stage')
            .prefetch_related('activities__activity__stage')
            .filter(pk=pk).first()
        )
        if project is None:
            return MyResponse.error(message='Proyecto no encontrado.', status_code=404)

        # Lo que el proyecto tiene marcado, por actividad.
        state = {pa.activity_id: pa for pa in project.activities.all()}

        stages = []
        for stage in Stage.objects.filter(is_active=True):
            activities = []
            for act in stage.activities.filter(is_active=True).order_by('order', 'code'):
                pa = state.get(act.id)
                # Una elegible sin fila no aplica todavía a este proyecto.
                applies = (not act.is_optional) or (pa is not None)
                activities.append({
                    **StageActivitySerializer(act).data,
                    'applies': applies,
                    'is_confirmed': project.is_activity_confirmed(act, state),
                    'confirmed_at': pa.confirmed_at if pa else None,
                })

            stages.append({
                **StageSerializer(stage).data,
                'progress': project.stage_progress(stage),
                'activities': activities,
            })

        return MyResponse.success(
            data={
                'project': ProjectSerializer(project).data,
                'selections_complete': project.selections_complete,
                'stages': stages,
            },
            message='Detalle del proyecto.',
        )


class ProjectActivityToggleView(APIView):
    """`POST /projects/<id>/activities/<activity_id>/` — marca o desmarca.

    Es la casilla del checklist. Con `applies` se agrega o se quita una
    actividad elegible del proyecto; con `is_confirmed` se marca hecha.
    """

    @staticmethod
    def _reloaded(project):
        """Vuelve a leer el proyecto con sus actividades ya cargadas.

        Hay que releerlo **después** de tocar la base: el avance recorre
        `project.activities`, y si esa lista se cargó antes del cambio,
        devolvería el porcentaje anterior.
        """
        return (
            Project.objects
            .prefetch_related('activities__activity')
            .get(pk=project.pk)
        )

    def post(self, request, pk, activity_id):
        project = Project.objects.filter(pk=pk).first()
        if project is None:
            return MyResponse.error(message='Proyecto no encontrado.', status_code=404)

        activity = StageActivity.objects.filter(pk=activity_id, is_active=True).first()
        if activity is None:
            return MyResponse.error(message='Actividad no encontrada.', status_code=404)

        applies = request.data.get('applies')
        confirmed = request.data.get('is_confirmed')

        # Quitar del proyecto una actividad elegible.
        if applies is False:
            if not activity.is_optional:
                return MyResponse.error(
                    message=(
                        f'"{activity.name}" aplica a todo proyecto y no se '
                        f'puede quitar.'
                    ),
                    status_code=400,
                )
            project.activities.filter(activity=activity).delete()
            return MyResponse.success(
                data={'progress': self._reloaded(project).progress},
                message='Actividad retirada del proyecto.',
            )

        if confirmed is not None and activity.is_derived:
            return MyResponse.error(
                message=(
                    f'"{activity.name}" no se confirma a mano: se marca sola '
                    f'cuando el proyecto elige sus actividades en todas las '
                    f'etapas que lo permiten.'
                ),
                status_code=400,
            )

        pa, _ = ProjectActivity.objects.get_or_create(project=project, activity=activity)

        if confirmed is not None:
            pa.is_confirmed = bool(confirmed)
            pa.confirmed_at = timezone.now() if pa.is_confirmed else None
            pa.save(update_fields=['is_confirmed', 'confirmed_at', 'updated_at'])

        fresh = self._reloaded(project)
        return MyResponse.success(
            data={
                'is_confirmed': pa.is_confirmed,
                'stage_progress': fresh.stage_progress(activity.stage),
                'progress': fresh.progress,
            },
            message='Actividad actualizada.',
        )


class StageMetricsView(APIView):
    """`GET /metrics/` — cuántos proyectos hay en cada etapa.

    Son las tarjetas de arriba de la pantalla. Se devuelven **todas** las
    etapas, incluidas las que están en cero: la tarjeta tiene que aparecer
    igual, si no la fila de métricas cambia de ancho según los datos.
    """

    def get(self, request):
        counts = {}
        for row in Project.objects.values('stage__code'):
            code = row['stage__code']
            if code:
                counts[code] = counts.get(code, 0) + 1

        data = [
            {
                'code': stage.code,
                'name': stage.name,
                'color': stage.color,
                'order': stage.order,
                'count': counts.get(stage.code, 0),
            }
            for stage in Stage.objects.filter(is_active=True)
        ]
        return MyResponse.success(data=data, message='Métricas por etapa.')
