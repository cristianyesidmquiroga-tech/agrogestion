import uuid
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Query

from app.core.etiquetas import ESTADISTICAS
from app.dependencies import SoloAdmin
from app.routers.dependencias import BD, Pagina, armar_pagina
from app.schemas.common import Page
from app.schemas.estadisticas import (
    CosechaRegistrada,
    CostosGenerales,
    EstadisticaCultivo,
    EstadisticaZona,
    InventarioGeneral,
    ManoDeObraGeneral,
    ProcesosGeneral,
    Productor,
    PuntoMensual,
    ResumenGeneral,
    SiembraRegistrada,
)
from app.services import estadisticas_cultivos_service as cultivos_zonas
from app.services import estadisticas_operacion_service as operacion
from app.services import estadisticas_produccion_service as produccion
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


@router.get("/produccion", response_model=Page[CosechaRegistrada], summary="Cosechas registradas")
async def producciones(
    db: BD,
    _: SoloAdmin,
    pag: Pagina,
    cultivo_id: uuid.UUID | None = None,
    zona: Annotated[str | None, Query(min_length=2, max_length=5)] = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> Page[CosechaRegistrada]:
    items, total = await produccion.producciones(
        db, cultivo_id, zona, desde, hasta, pag.skip, pag.limit
    )
    return armar_pagina(items, total, pag)


@router.get("/siembras", response_model=Page[SiembraRegistrada], summary="Siembras registradas")
async def siembras(
    db: BD,
    _: SoloAdmin,
    pag: Pagina,
    cultivo_id: uuid.UUID | None = None,
    estado: Literal["planeada", "en_curso", "cerrada", "cancelada"] | None = None,
    zona: Annotated[str | None, Query(min_length=2, max_length=5)] = None,
) -> Page[SiembraRegistrada]:
    items, total = await produccion.siembras(db, cultivo_id, estado, zona, pag.skip, pag.limit)
    return armar_pagina(items, total, pag)


@router.get("/productores", response_model=list[Productor], summary="Quién produce más")
async def productores(db: BD, _: SoloAdmin) -> list[Productor]:
    return await produccion.productores(db)


@router.get("/mano-de-obra", response_model=ManoDeObraGeneral, summary="Trabajadores y jornales")
async def mano_de_obra(db: BD, _: SoloAdmin) -> ManoDeObraGeneral:
    return await operacion.mano_de_obra(db)


@router.get("/inventario", response_model=InventarioGeneral, summary="Insumos y consumos")
async def inventario(db: BD, _: SoloAdmin) -> InventarioGeneral:
    return await operacion.inventario(db)


@router.get("/procesos", response_model=ProcesosGeneral, summary="Procesos de transformación")
async def procesos(db: BD, _: SoloAdmin) -> ProcesosGeneral:
    return await operacion.procesos(db)
