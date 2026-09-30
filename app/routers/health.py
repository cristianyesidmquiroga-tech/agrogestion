"""Salud del servicio. No consulta la base de datos a propósito."""
from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse, summary="Salud del servicio")
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name, version="1.0.0")
