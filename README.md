# AgroGestion

<details>
<summary><b>Read this in English</b></summary>

REST API for crop and livestock management built with FastAPI, PostgreSQL 16, SQLAlchemy 2.0 and `asyncpg`. It covers farms and plots, a crop catalogue with profiles, plantings and cycles, plant counts, nursery batches, adverse events, knowledge base, assistant, regional news, labour, inputs, harvests, processes, accounting and livestock.

Quick start: copy `.env.example` to `.env`, run `python -m pip install -e ".[dev]"`, then `alembic upgrade head` and `uvicorn app.main:app --reload`. Interactive docs are served at `/docs` with a login panel. Run `./verificar.ps1` before every pull request.

</details>

API REST para la gestión de cultivos y ganadería con FastAPI, PostgreSQL 16, SQLAlchemy 2.0 y `asyncpg`. Cubre fincas y lotes, catálogo de cultivos con perfil, siembras y ciclos, conteo de plantas, vivero, eventos adversos, base de conocimiento, asistente, noticias regionales, mano de obra, insumos, cosechas, procesos, contabilidad y pecuario.

## Inicio

1. Copiar `.env.example` a `.env` y cambiar los secretos.
2. Crear el entorno: `python -m pip install -e ".[dev]"`.
3. Aplicar migraciones: `alembic upgrade head`.
4. Ejecutar: `uvicorn app.main:app --reload`.
5. Datos de ejemplo en SQLite: `python -m scripts.demo` (usa `SEED_PASSWORD` del `.env`).

En Windows, ejecute `iniciar_local.bat` con doble clic. La primera vez crea `.env` con una clave JWT aleatoria, prepara `.venv` e instala las dependencias; luego aplica las migraciones, prepara `admin@demo.com` con contraseña `1234` y arranca FastAPI. La contraseña se restablece en cada arranque local y no debe usarse en producción. Requiere Python 3.12 o superior y conexión a internet para instalar dependencias.

### Administrador inicial en Coolify

En las variables de entorno del servicio configure `ADMIN_EMAIL` con el correo deseado y `ADMIN_PASSWORD` con una contraseña segura de al menos 10 caracteres. El contenedor crea ese usuario con rol `admin` después de aplicar las migraciones y antes de iniciar la API. Configure ambas variables o ninguna. Si ya existe una cuenta admin con ese correo, el arranque la deja intacta: cambiar estas variables después no restablece su contraseña. No use las credenciales locales `admin@demo.com` / `1234` en producción.

La documentación interactiva está en `/docs`: inicie sesión en el panel superior y las pruebas usan ese perfil. `GET /auth/me` devuelve las funciones que cada perfil puede usar.

## Estructura

- `app/core`: configuración, base de datos, seguridad y errores.
- `app/models`: entidades; `entities.py` trae lo transaccional y el resto, el dominio agrícola.
- `app/routers`, `app/services`, `app/schemas`: capas por recurso.
- `alembic/versions`: migraciones 0001 a 0006.
- `tests/modulos`, `tests/roles`, `tests/vistas`: pruebas por módulo, por rol y por pantalla.
- `docs/`: contrato de la API para el cliente móvil, generado con `python -m scripts.exportar_contrato`.

Antes de cada Pull Request: `./verificar.ps1` (pytest, ruff, mypy, bandit y verificación del contrato).
