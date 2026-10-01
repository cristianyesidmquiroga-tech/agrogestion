"""Punto de entrada. Solo monta routers; la lógica vive en services/."""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.etiquetas import ETIQUETAS
from app.core.exceptions import registrar_manejadores
from app.core.registro import configurar_registro, instalar
from app.routers import (
    acceso,
    conocimiento,
    consultas,
    cuenta,
    cultivos,
    documentacion,
    eventos,
    health,
    inicio,
    noticias,
    propagacion,
    reportes,
    siembras,
)
from app.schemas.common import ErrorRespuesta

settings = get_settings()

DESCRIPCION = (
    "API para gestionar cultivos de principio a fin: siembras, ciclos, conteo de plantas, "
    "vivero, riesgos y eventos adversos. Todos los errores usan el mismo formato: decida "
    "siempre con el campo `error`, nunca con `message`."
)


RESPUESTAS_ERROR: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorRespuesta, "description": "Sin sesión o sesión vencida."},
    403: {"model": ErrorRespuesta, "description": "El rol no tiene permiso."},
    404: {"model": ErrorRespuesta, "description": "No existe o no pertenece al usuario."},
    409: {"model": ErrorRespuesta, "description": "Choca con algo que ya existe."},
    422: {"model": ErrorRespuesta, "description": "Datos inválidos o regla de negocio."},
}


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description=DESCRIPCION,
        openapi_tags=ETIQUETAS,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
        allow_credentials=False,
        max_age=600,
    )
    registrar_manejadores(app)
    instalar(app, configurar_registro(settings.log_level))
    app.include_router(documentacion.router)
    for router in (
        acceso.router,
        cuenta.router,
        inicio.router,
        cultivos.router,
        siembras.router,
        propagacion.router,
        eventos.router,
        reportes.router,
        conocimiento.router,
        consultas.router,
        noticias.router,
    ):
        app.include_router(router, prefix=settings.api_prefix, responses=RESPUESTAS_ERROR)
    app.include_router(health.router)
    return app


app = create_app()
