"""Punto de entrada. Solo monta routers; la lógica vive en services/."""
from fastapi import FastAPI

from app.core.config import get_settings
from app.routers import health

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    app.include_router(health.router)
    return app


app = create_app()
