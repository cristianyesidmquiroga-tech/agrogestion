"""Reportes. Dinero, mano de obra y procesos figuran como no disponibles hasta que existan."""

import uuid
from datetime import date

from fastapi import APIRouter

from app.core.security import Autenticado, EscribeProduccion, LeeProduccion
from app.routers.dependencias import BD
from app.schemas.inicio import (
    ReporteCronograma,
    ReporteDisponible,
    ReporteEventos,
    ReporteIndices,
)
from app.services import reporte_service as servicio

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("", response_model=list[ReporteDisponible], summary="Reportes que puedo ver")
async def catalogo(usuario: Autenticado) -> list[ReporteDisponible]:
    return servicio.catalogo(usuario)


@router.get("/indices", response_model=ReporteIndices, summary="Índices por planta de mis siembras")
async def indices(
    db: BD, usuario: LeeProduccion, finca_id: uuid.UUID | None = None
) -> ReporteIndices:
    return await servicio.indices(db, usuario, finca_id)


@router.get("/cronograma", response_model=ReporteCronograma, summary="Tiempos de mis ciclos")
async def cronograma(
    db: BD, usuario: LeeProduccion, finca_id: uuid.UUID | None = None
) -> ReporteCronograma:
    return await servicio.cronograma(db, usuario, finca_id)


@router.get("/eventos", response_model=ReporteEventos, summary="Eventos adversos y su costo")
async def eventos(
    db: BD,
    usuario: EscribeProduccion,
    finca_id: uuid.UUID | None = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> ReporteEventos:
    return await servicio.eventos(db, usuario, finca_id, desde, hasta)
