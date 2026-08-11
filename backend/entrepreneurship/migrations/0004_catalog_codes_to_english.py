"""Pasa los `code` del catálogo a inglés.

El `code` es un identificador: se usa en el filtro de la API y viaja en la URL
de la pantalla de etapa. El `name` no se toca — es lo que se lee en pantalla y
sigue en español.

Sin esta migración, `seed_stages` con los códigos nuevos crearía filas
duplicadas y los proyectos existentes quedarían apuntando a las viejas.

Solo renombra si el código viejo existe y el nuevo no, así que correrla dos
veces no rompe nada.
"""
from django.db import migrations

STAGES = {
    'PRE_INCUBACION': 'PRE_INCUBATION',
    'INCUBACION': 'INCUBATION',
    'POST_INCUBACION': 'POST_INCUBATION',
}

ACTIVITIES = {
    'IDEA_CONVOCATORIA': 'IDEA_CALL',
    'IDEA_FORMULACION': 'IDEA_FORMULATION',
    'IDEA_EVALUACION': 'IDEA_EVALUATION',
    'IDEA_APROBACION': 'IDEA_APPROVAL',
    'PRE_TALLER': 'PRE_WORKSHOP',
    'INC_MENTORIAS': 'INC_MENTORING',
    'INC_MONITOREO': 'INC_MONITORING',
    'PITCH_EXPOSICION': 'PITCH_PRESENTATION',
    'PITCH_EVALUACION': 'PITCH_EVALUATION',
    'PITCH_CIERRE': 'PITCH_CLOSING',
    'PITCH_ARTICULACION': 'PITCH_ARTICULATION',
    'POST_IMPLEMENTACION': 'POST_IMPLEMENTATION',
    'POST_MONITOREO': 'POST_MONITORING',
    'POST_ARTICULACION': 'POST_ARTICULATION',
}


def _rename(model, mapping):
    """Renombra códigos uno por uno. `code` es único: si el destino ya está
    ocupado se deja la fila como está en vez de reventar la migración."""
    for old, new in mapping.items():
        if model.objects.filter(code=new).exists():
            continue
        model.objects.filter(code=old).update(code=new)


def to_english(apps, schema_editor):
    _rename(apps.get_model('entrepreneurship', 'Stage'), STAGES)
    _rename(apps.get_model('entrepreneurship', 'StageActivity'), ACTIVITIES)


def to_spanish(apps, schema_editor):
    _rename(
        apps.get_model('entrepreneurship', 'Stage'),
        {new: old for old, new in STAGES.items()},
    )
    _rename(
        apps.get_model('entrepreneurship', 'StageActivity'),
        {new: old for old, new in ACTIVITIES.items()},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('entrepreneurship', '0003_stageactivity_is_derived'),
    ]

    operations = [
        migrations.RunPython(to_english, to_spanish),
    ]
