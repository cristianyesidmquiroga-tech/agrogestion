from typing import Annotated, Literal

from fastapi import APIRouter, Query

from app.core.etiquetas import ESTADISTICAS
from app.dependencies import SoloAdmin
from app.routers.dependencias import BD
from app.schemas.estadisticas import (
    CostosGenerales,
    EstadisticaCultivo,
    EstadisticaZona,
    PuntoMensual,
    ResumenGeneral,
)
from app.services import estadisticas_cultivos_service as cultivos_zonas
from app.services import estadisticas_service as servicio

router = APIRouter(prefix="/estadisticas", tags=[ESTADISTICAS])


@router.get("/resumen", response_model=ResumenGeneral, summary="Totales de toda la aplicación")
async def resumen(db: BD, _: SoloAdmin) -> ResumenGeneral:
    return await servicio.resumen(db)


@router.get("/crecimiento", response_model=list[PuntoMensual], summary="Crecimiento por mes")
async def crecimiento(
    db: BD, _: SoloAdmin, meses: Annotated[int, Query(ge=1, le=36)] = 12
) -> list[PuntoMensual]:
    return await servicio.crecimiento(db, meses)


@router.get("/costos", response_model=CostosGenerales, summary="Gastos e ingresos por categoría")
async def costos(db: BD, _: SoloAdmin) -> CostosGenerales:
    return await servicio.costos(db)


@router.get("/cultivos", response_model=list[EstadisticaCultivo], summary="Comparativo por cultivo")
async def cultivos(db: BD, _: SoloAdmin) -> list[EstadisticaCultivo]:
    return await cultivos_zonas.cultivos(db)


@router.get("/zonas", response_model=list[EstadisticaZona], summary="Comparativo por zona")
async def zonas(
    db: BD, _: SoloAdmin, nivel: Literal["departamento", "municipio"] = "departamento"
) -> list[EstadisticaZona]:
    return await cultivos_zonas.zonas(db, nivel)
