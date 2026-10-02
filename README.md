# AgroGestion

API REST para la gestión agrícola con FastAPI, PostgreSQL 16, SQLAlchemy 2.0 y `asyncpg`.

## Inicio

1. Copiar `.env.example` a `.env` y cambiar los secretos.
2. Crear el entorno: `python -m pip install -e ".[dev]"`.
3. Aplicar migraciones SQLite: `alembic upgrade head`.
4. Ejecutar: `uvicorn app.main:app --reload`.

La API expone `GET /health`, autenticación en `/auth` y gestión aislada de `/fincas` y `/lotes`. Ejecutar `./verificar.ps1` antes de cada Pull Request.

El entorno actual usa `sqlite+aiosqlite`; la URL puede cambiarse mediante `DATABASE_URL` cuando se habilite PostgreSQL.

## Despliegue en Coolify usando Docker Compose

Configurar el recurso desde `docker-compose.yml`, seleccionar el servicio `agrogestion` y asignarle un dominio en el puerto interno `8000` (Coolify enruta el tráfico al puerto expuesto por Compose). Definir `JWT_SECRET` y `FIELD_ENCRYPTION_KEY` como variables **runtime** del servicio. Configurar `ALLOWED_ORIGINS` con los orígenes autorizados y `ALERT_ALLOWED_HOSTS` solo si se habilitan fuentes regionales.

El contenedor ejecuta `alembic upgrade head` al iniciar. SQLite se guarda en `/data/agrogestion.db`, en el volumen persistente `agrogestion_data`; conservar ese volumen entre despliegues.

Generar valores para secretos con:

```sh
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

La clave Fernet debe mantenerse estable entre despliegues para poder descifrar los datos ya guardados. Para probar localmente, cargar ambas variables y ejecutar `docker compose up --build`.
