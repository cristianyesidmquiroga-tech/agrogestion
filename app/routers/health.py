"""Salud del servicio: /health dice si el proceso vive; /health/ready, si puede trabajar."""

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.etiquetas import SALUD
from app.core.exceptions import ServicioNoListo
from app.routers.dependencias import BD
from app.schemas.common import HealthResponse, ReadyResponse

router = APIRouter(tags=[SALUD])
settings = get_settings()


@router.get("/health", response_model=HealthResponse, summary="Salud del servicio")
async def health() -> HealthResponse:
    """No consulta la base de datos a propósito: responde si el servidor está vivo."""
    return HealthResponse(status="ok", service=settings.app_name, version="1.0.0")


@router.get(
    "/health/ready", response_model=ReadyResponse, summary="El servicio está listo para trabajar"
)
async def ready(db: BD) -> ReadyResponse:
    try:
        await db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise ServicioNoListo("El servicio aún no puede atender. Intente en un momento.") from None
    return ReadyResponse(
        status="ok", service=settings.app_name, version="1.0.0", base_de_datos="ok"
    )
