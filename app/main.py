"""Punto de entrada. Solo monta routers; la lógica vive en services/."""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exceptions import registrar_manejadores
from app.core.registro import configurar_registro, instalar
from app.routers import (
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

ETIQUETAS = [
    {
        "name": "cultivos",
        "description": "Catálogo de cultivos con su perfil y catálogo de riesgos.",
    },
    {"name": "siembras", "description": "Siembras, ciclos, conteo de plantas e indicadores."},
    {"name": "propagacion", "description": "Vivero: propagación por semilla, esqueje u otros."},
    {"name": "eventos", "description": "Heladas, sequías, granizo, plagas y otros eventos."},
    {"name": "cuenta", "description": "Glosario, política de datos y consentimiento."},
    {
        "name": "conocimiento",
        "description": "Biblioteca de problemas sanitarios revisados por expertos.",
    },
    {
        "name": "asistente",
        "description": "Consultas sobre fichas validadas; no inventa diagnósticos.",
    },
    {"name": "noticias", "description": "Noticias de su región que vencen solas."},
    {"name": "inicio", "description": "Lo de hoy y avisos de riesgo por fase."},
    {"name": "reportes", "description": "Reportes con los datos disponibles."},
    {"name": "health", "description": "Salud del servicio."},
]

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
    app.include_router(health.router)
    app.include_router(documentacion.router)
    for router in (
        cultivos.router,
        siembras.router,
        propagacion.router,
        eventos.router,
        cuenta.router,
        inicio.router,
        reportes.router,
        conocimiento.router,
        consultas.router,
        noticias.router,
    ):
        app.include_router(router, prefix=settings.api_prefix, responses=RESPUESTAS_ERROR)
    return app


app = create_app()
