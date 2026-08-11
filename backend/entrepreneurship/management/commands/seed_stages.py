"""Siembra las etapas del proceso de emprendimiento y sus actividades.

Todo sale del mockup del proceso. Idempotente por `code`: no pisa lo que la
institución haya ajustado, solo crea lo que falte.

Las actividades marcadas como **elegibles** no aplican a todo proyecto: se
escogen por emprendimiento y solo entonces cuentan para el avance.

    python manage.py tenant_command seed_stages --schema=itb
"""
from django.core.management.base import BaseCommand

from entrepreneurship.models import Stage, StageActivity

# El `code` es identificador: va en inglés y viaja en la URL de la pantalla de
# etapa. El `name` es lo que se lee en pantalla y queda en español.
#
# (code, name, orden, color)
STAGES = [
    ('IDEA', 'Idea', 1, 'blue'),
    ('PRE_INCUBATION', 'Pre-incubación', 2, 'darkblue'),
    ('INCUBATION', 'Incubación', 3, 'orange'),
    ('PITCH', 'Pitch', 4, 'red'),
    ('POST_INCUBATION', 'Post-incubación', 5, 'green'),
]

# etapa -> [(code, name, es_elegible, es_derivada)]
# Derivada = no se confirma a mano; se marca sola. Solo la Formulación
# de la Idea lo es: ahí se eligen las actividades de las otras etapas.
ACTIVITIES = {
    'IDEA': [
        ('IDEA_CALL', 'Convocatoria a la presentación de ideas', False, False),
        ('IDEA_FORMULATION', 'Formulación de la Idea', False, True),
        ('IDEA_EVALUATION', 'Evaluación de la idea', False, False),
        ('IDEA_APPROVAL', 'Aprobación del proyecto', False, False),
    ],
    'PRE_INCUBATION': [
        ('PRE_WORKSHOP', 'Taller', False, False),
    ],
    'INCUBATION': [
        ('INC_WORKSHOP', 'Workshop', True, False),
        ('INC_SPEAKERS', 'Speakers', True, False),
        ('INC_BOOTCAMP', 'Bootcamp', True, False),
        ('INC_MENTORING', 'Mentorías', True, False),
        ('INC_COWORKING', 'Coworking', True, False),
        ('INC_NETWORKING', 'Networking', True, False),
        # Esta va siempre, a diferencia de las de arriba.
        ('INC_MONITORING', 'Monitoreo al proyecto', False, False),
    ],
    'PITCH': [
        ('PITCH_PRESENTATION', 'Exposición del Pitch', False, False),
        ('PITCH_EVALUATION', 'Evaluación del Pitch', False, False),
        ('PITCH_CLOSING', 'Cierre del Proyecto', False, False),
        ('PITCH_ARTICULATION', 'Articulación del Proyecto', False, False),
    ],
    'POST_INCUBATION': [
        ('POST_IMPLEMENTATION', 'Implementación del Emprendimiento', True, False),
        ('POST_MONITORING', 'Monitoreo al Emprendimiento', True, False),
        ('POST_ARTICULATION', 'Articulación del Emprendimiento', True, False),
    ],
}


class Command(BaseCommand):
    help = 'Siembra las etapas del proceso de emprendimiento y sus actividades.'

    def handle(self, *args, **options):
        stages = {}
        created = updated = 0

        for code, name, order, color in STAGES:
            stage, is_new = Stage.objects.update_or_create(
                code=code,
                defaults={'name': name, 'order': order, 'color': color},
            )
            stages[code] = stage
            created += int(is_new)
            updated += int(not is_new)

        act_created = act_updated = 0
        for stage_code, items in ACTIVITIES.items():
            stage = stages[stage_code]
            self.stdout.write(f'  {stage.order}. {stage.name}')
            for order, (code, name, optional, derived) in enumerate(items, start=1):
                _obj, is_new = StageActivity.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': name, 'stage': stage, 'order': order,
                        'is_optional': optional, 'is_derived': derived,
                    },
                )
                act_created += int(is_new)
                act_updated += int(not is_new)
                mark = 'derivada' if derived else ('elegible' if optional else 'fija')
                self.stdout.write(f'       {name}  ({mark})')

        self.stdout.write(self.style.SUCCESS(
            f'Etapas: creadas={created} actualizadas={updated} · '
            f'Actividades: creadas={act_created} actualizadas={act_updated}'
        ))
