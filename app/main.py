"""Punto de entrada. Solo monta routers; la lógica vive en services/."""

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.exceptions import registrar_manejadores
from app.routers import cuenta, cultivos, eventos, health, propagacion, siembras

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    registrar_manejadores(app)
    app.include_router(health.router)
    for router in (
        cultivos.router,
        siembras.router,
        propagacion.router,
        eventos.router,
        cuenta.router,
    ):
        app.include_router(router, prefix=settings.api_prefix)
    return app


app = create_app()
