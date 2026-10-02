# AgroGestion

API REST para la gestión agrícola con FastAPI, PostgreSQL 16, SQLAlchemy 2.0 y `asyncpg`.

## Inicio

1. Copiar `.env.example` a `.env` y cambiar los secretos.
2. Crear el entorno: `python -m pip install -e ".[dev]"`.
3. Aplicar migraciones SQLite: `alembic upgrade head`.
4. Ejecutar: `uvicorn app.main:app --reload`.

La API expone `GET /health`, autenticación en `/auth` y gestión aislada de `/fincas` y `/lotes`. Ejecutar `./verificar.ps1` antes de cada Pull Request.

El entorno actual usa `sqlite+aiosqlite`; la URL puede cambiarse mediante `DATABASE_URL` cuando se habilite PostgreSQL.

## Despliegue en Coolify

Seleccionar el tipo de aplicación **Dockerfile** y publicar el puerto `8000`. Configurar como mínimo `JWT_SECRET` y `FIELD_ENCRYPTION_KEY` en las variables de entorno de Coolify. El contenedor ejecuta `alembic upgrade head` al iniciar y almacena SQLite en `/data`; montar un volumen persistente en `/data`.

Para probar localmente: `docker compose up --build`.
