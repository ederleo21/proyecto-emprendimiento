# Outreach — Vinculación con la Sociedad

Microservicio de vinculación con la sociedad. Monorepo independiente: backend Django + frontend
SvelteKit, con su propia base de datos y su propio `docker compose`.

Vive fuera del monorepo de InnoTech y no depende de nada de él: se levanta,
se desarrolla y se prueba solo. Todo lo que necesita de aquel ecosistema
—firma del JWT, lista de instituciones— entra por configuración, no por
imports.

---

## Levantar

```bash
cd outreach
cp .env.example .env
docker compose up -d --build
```

| Qué | Dónde |
|---|---|
| API | http://localhost:8100/api/v1/ |
| Health | http://localhost:8100/api/v1/health/ |
| Frontend | http://localhost:5180 |
| Base de datos | localhost:5434 (`outreach` / postgres / postgres) |

Los puertos están corridos (8100, 5180, 5434) para **no chocar** con el
stack de InnoTech si lo tienes levantado al mismo tiempo. La base va en 5434
porque 5433 ya lo ocupa el `db` de InnoTech.

---

## Por qué está armado así

Se copiaron las convenciones de los microservicios de InnoTech para que este
servicio pueda enchufarse al ecosistema el día que se pida, sin reescribirlo:

**Multi-tenant con `django-tenants`.** Un schema de PostgreSQL por institución.
Igual que `academic_service` y `admission_service`.

**Valida el JWT del IAM de InnoTech** con la misma firma (`JWT_SIGNING_KEY`).
El usuario que viaja en ese token no se guarda en ninguna tabla: vive en
memoria durante el request (`core/authentication.py`). Entre servicios se usa
`X-Internal-Secret`.

**Y además tiene acceso propio**, que es la única divergencia deliberada con
los demás microservicios. La app `accounts` emite sus propios tokens desde
`/api/v1/auth/sign-in/`, con los mismos claims que el IAM, para que el proyecto
se pueda desarrollar sin levantar aquel stack. El día de la integración eso
pasa a ser solo modo desarrollo: la identidad la manda el IAM.

**Respuestas con envoltorio.** Todo endpoint responde
`{status, message, data, errors}` vía `MyResponse`. El frontend de InnoTech ya
espera esa forma.

**Sin conexión directa a otras bases.** Si más adelante necesita datos de otro
servicio (carreras, estudiantes, docentes), se replican en tablas locales
alimentadas por REST o Kafka. Nunca se consulta la BD ajena.

### `core/` es una copia reducida, a propósito

Los servicios de InnoTech importan `core_shared`, un paquete que vive en aquel
monorepo (2.291 líneas: PDF, Google Cloud Storage, Kafka DLQ, caché…). Este
proyecto tiene que poder salir de ahí, así que `core/` trae **solo lo que usa**:

| Archivo | Equivale a |
|---|---|
| `core/my_base.py` | `core_shared.my_base` — `BaseModel`, `BasePerson` |
| `core/my_response.py` | `core_shared.my_response` — `MyResponse` |
| `core/authentication.py` | `core_shared.authentication` — JWT + `X-Internal-Secret` |
| `core/helpers/service_helper.py` | `core_shared.helpers.service_helper` |

Las firmas se mantuvieron idénticas, así que al integrarse se cambian los
imports por `core_shared.*` sin tocar el dominio.

> **Con una excepción: `CatalogBase` no existe en `core_shared`.** Se verificó
> contra el monorepo: allá cada servicio se lo define por su cuenta
> (`academic_service` lo tiene en `curricular_design/models/catalog/base.py`).
> Como `Stage` y `StageActivity` heredan de él, esa clase se queda en `core/`
> aunque el resto migre.

---

## Estructura

```
outreach/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── config/            settings, urls
│   ├── core/              BaseModel, MyResponse, autenticación (ver arriba)
│   ├── tenants/           Tenant, Domain, middleware, sync desde IAM
│   ├── accounts/          User propio y sus tokens (solo desarrollo)
│   ├── entrepreneurship/  Proyecto de Emprendimiento: etapas, actividades, avance
│   ├── api/v1/            rutas de la API
│   └── scripts/           create_db.py
└── frontend/              SvelteKit + Svelte 5
```

El único dominio modelado es el **Proyecto de Emprendimiento**. Cada módulo
nuevo entra como app Django en `TENANT_APPS` y cuelga sus rutas de
`api/v1/urls.py`.

### Lo que el Proyecto de Emprendimiento sí resuelve, y lo que no

Cinco etapas con sus actividades, y el avance calculado —nunca guardado— como
confirmadas sobre aplicables. Hay tres clases de actividad: **fijas** (aplican
siempre), **elegibles** (cuentan solo si el proyecto las escogió) y
**derivadas** (no se confirman a mano; se marcan solas cuando el proyecto ya
eligió en todas las etapas que admiten elección).

Lo que **no** está, porque el proceso no lo tiene definido: quién puede
confirmar una actividad, qué entregable exige cada una, si hay que cerrar una
etapa para abrir la siguiente, y qué mueve un proyecto de etapa. Ese último
hueco se ve en pantalla: `Project.stage` nunca se asigna, así que las tarjetas
de métricas salen en cero.

---

## Comandos

```bash
# Migraciones (el esquema público y el de cada tenant van por separado)
docker compose exec backend python manage.py migrate_schemas --shared
docker compose exec backend python manage.py migrate_schemas

# Traer la lista de instituciones desde el IAM de InnoTech
docker compose exec backend python manage.py sync_tenants

# Crear un tenant a mano, sin IAM
docker compose exec backend python manage.py create_tenant_local itb "Instituto Tecnológico Bolivariano"

# Usuario para entrar mientras no haya IAM
docker compose exec backend python manage.py create_admin admin --password admin123 --schema itb

# Sembrar las etapas y actividades del proceso (idempotente)
docker compose exec backend python manage.py tenant_command seed_stages --schema=itb

# Tests
docker compose exec backend python manage.py test entrepreneurship

# Logs
docker compose logs -f backend
```

> Como en los otros servicios, **cambiar rutas o `settings.py` exige reiniciar**
> el contenedor: el autoreload de Django no ve esos cambios a través del volumen
> montado en Windows.
> ```bash
> docker compose restart backend
> ```

---

## Integrarlo con InnoTech

Nada de esto es necesario para desarrollar, pero está previsto:

1. **JWT** — poner en `.env` el mismo `JWT_SIGNING_KEY` que usa el IAM. Los
   tokens que ya emite empiezan a valer acá.
2. **Tenants** — apuntar `SERVICE_IAM_URL` al IAM y correr `sync_tenants`.
3. **Red** — los dos `docker compose` crean su propia red, así que hoy este
   servicio no resuelve `iam-service` y `sync_tenants` falla. Hay que declarar
   la red de InnoTech como `external`.
4. **Permisos** — declarar el catálogo en `permissions.py` y registrarlo en IAM,
   igual que hace `academic_service` con `sync_permissions`. Hoy no existe:
   todos los endpoints son `IsAuthenticated` a secas.
5. **Frontend** — allá los micro-frontends son apps SvelteKit servidas bajo
   `/mfe/<nombre>/` y embebidas en un `<iframe>` por `shell-sv`, que les pasa
   la sesión en el fragmento de la URL (`#token=…&refresh_token=…`). Este
   frontend ya sabe leerla — ver `src/lib/session.ts` — y toma su prefijo de
   las variables `BASE_PATH` y `ASSET_BASE`. Falta moverlo a `frontend/apps/`
   del monorepo y agregarle su `nginx-outreach.conf`.

   > La federación de módulos que aparece configurada en `shell-sv` **no se
   > usa**: declara `remotes: {}`. El acople real es por iframe.
