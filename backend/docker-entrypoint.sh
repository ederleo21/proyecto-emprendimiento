#!/bin/sh
# Arranque del backend. Sin argumentos levanta el servidor; con argumentos
# ejecuta el comando que se le pase (`docker compose run backend <cmd>`).
set -e

mkdir -p /app/media /app/staticfiles
chown -R appuser:appuser /app/media /app/staticfiles 2>/dev/null || true

echo "Esperando a postgres..."
while ! python -c "import socket; socket.create_connection(('db', 5432))" 2>/dev/null; do
  sleep 0.3
done
echo "PostgreSQL disponible."

if [ $# -eq 0 ]; then
    echo "Asegurando que la base de datos exista..."
    python scripts/create_db.py

    echo "Aplicando migraciones..."
    # Dos pasadas: `--shared` toca el schema public (donde vive el registro de
    # instituciones) y la segunda toca el schema de cada institución. Sin la
    # segunda, un modelo nuevo solo llegaría a las que se creen después.
    python manage.py migrate_schemas --shared
    python manage.py migrate_schemas --tenant \
        || echo "[entrypoint] migrate_schemas --tenant falló (¿aún no hay instituciones?), se continúa."

    # IAM es la fuente de verdad de las instituciones. Si no está levantado se
    # sigue igual: se puede crear una a mano con create_tenant_local.
    echo "Sincronizando instituciones desde IAM..."
    python manage.py sync_tenants \
        || echo "[entrypoint] sync_tenants falló (IAM no disponible), se continúa."

    # Si tras lo anterior no hay ninguna institución, se crea la del `.env` con
    # su catálogo. Así un clon recién levantado ya tiene algo que mostrar en vez
    # de una pantalla vacía y un comando que buscar en el README.
    python manage.py ensure_default_tenant \
        || echo "[entrypoint] ensure_default_tenant falló, se continúa."

    echo "Arrancando servidor..."
    # `--noreload`: el autoreload no ve los cambios a través del bind-mount en
    # Windows y solo duplica el proceso. Los cambios exigen reiniciar igual.
    exec gosu appuser python manage.py runserver --noreload 0.0.0.0:8000
else
    echo "Ejecutando: $@"
    exec gosu appuser "$@"
fi
