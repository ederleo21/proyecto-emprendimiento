"""Crea la base de datos si no existe.

El contenedor de Postgres solo crea la base indicada en `POSTGRES_DB`. Si se
cambia `DATABASE_URL` a otro nombre, Django arrancaría contra una base
inexistente. Esto lo resuelve antes de migrar.

Se conecta a la base `postgres` (siempre existe) para poder ejecutar el CREATE.
"""
import os
import sys


def create_db():
    db_url = os.environ.get(
        'DATABASE_URL', 'postgres://postgres:postgres@db:5432/outreach',
    )

    parts = db_url.rsplit('/', 1)
    if len(parts) != 2:
        print(f'DATABASE_URL con formato inesperado: {db_url}')
        return
    admin_url = parts[0] + '/postgres'
    db_name = parts[1].split('?')[0]

    print(f"Conectando a {admin_url} para asegurar la existencia de '{db_name}'...")

    try:
        import psycopg
        connection = psycopg.connect(admin_url)
    except ImportError:
        try:
            import psycopg2
            connection = psycopg2.connect(admin_url)
        except ImportError:
            print('Error: no se encontró psycopg ni psycopg2.')
            return
    except Exception as exc:
        print(f'No se pudo conectar a Postgres: {exc}')
        sys.exit(1)

    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
        if cursor.fetchone():
            print(f"La base de datos '{db_name}' ya existe.")
        else:
            print(f"Creando la base de datos '{db_name}'...")
            try:
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                print(f"Base de datos '{db_name}' creada.")
            except Exception as exc:
                # Otro contenedor pudo haberla creado en paralelo.
                if 'already exists' in str(exc).lower():
                    print(f"La base '{db_name}' ya existía (creada en paralelo).")
                else:
                    raise
    connection.close()


if __name__ == '__main__':
    create_db()
