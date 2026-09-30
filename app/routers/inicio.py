"""Pantalla de inicio y avisos de riesgo."""

from fastapi import APIRouter

from app.core.security import Autenticado, LeeProduccion
from app.routers.dependencias import BD
from app.schemas.inicio import AvisosSalida, InicioSalida
from app.services import aviso_service, inicio_service

router = APIRouter(tags=["inicio"])


@router.get("/inicio", response_model=InicioSalida, summary="Lo de hoy")
async def inicio(db: BD, usuario: Autenticado) -> InicioSalida:
    return await inicio_service.resumen(db, usuario)


@router.get(
    "/avisos", response_model=AvisosSalida, summary="Avisos de riesgo según la fase de sus cultivos"
)
async def avisos(db: BD, usuario: LeeProduccion) -> AvisosSalida:
    return await aviso_service.avisos(db, usuario)
