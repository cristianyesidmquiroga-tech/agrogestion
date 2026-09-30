"""Siembras, ciclos, conteo de plantas e indicadores."""

import uuid

from fastapi import APIRouter, status

from app.core.catalogos import EstadoSiembra
from app.core.security import EscribeProduccion, LeeProduccion
from app.routers.dependencias import BD, Pagina, armar_pagina
from app.schemas.common import Page
from app.schemas.siembra import (
    CerrarCicloEntrada,
    CicloCrear,
    CicloSalida,
    ConteoCrear,
    ConteoSalida,
    CronogramaSalida,
    IndicesSalida,
    IniciarEntrada,
    NecesidadSalida,
    SiembraCrear,
    SiembraResumen,
    SiembraSalida,
)
from app.services import conteo_service, siembra_service

router = APIRouter(tags=["siembras"])


@router.get("/siembras", response_model=Page[SiembraResumen], summary="Mis siembras")
async def listar_siembras(
    db: BD,
    usuario: LeeProduccion,
    pag: Pagina,
    estado: EstadoSiembra | None = None,
    finca_id: uuid.UUID | None = None,
) -> Page[SiembraResumen]:
    items, total = await siembra_service.listar(db, usuario, estado, finca_id, pag.skip, pag.limit)
    return armar_pagina([SiembraResumen.model_validate(s) for s in items], total, pag)


@router.post(
    "/siembras",
    response_model=SiembraSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Planear una siembra",
)
async def crear_siembra(db: BD, usuario: EscribeProduccion, datos: SiembraCrear) -> SiembraSalida:
    return SiembraSalida.model_validate(await siembra_service.crear(db, usuario, datos))


@router.get(
    "/siembras/{siembra_id}", response_model=SiembraSalida, summary="Detalle de una siembra"
)
async def ver_siembra(db: BD, usuario: LeeProduccion, siembra_id: uuid.UUID) -> SiembraSalida:
    return SiembraSalida.model_validate(await siembra_service.obtener(db, usuario, siembra_id))


@router.post(
    "/siembras/{siembra_id}/iniciar", response_model=SiembraSalida, summary="Iniciar una siembra"
)
async def iniciar_siembra(
    db: BD, usuario: EscribeProduccion, siembra_id: uuid.UUID, datos: IniciarEntrada | None = None
) -> SiembraSalida:
    fecha = datos.fecha_inicio if datos else None
    return SiembraSalida.model_validate(
        await siembra_service.iniciar(db, usuario, siembra_id, fecha)
    )


@router.post(
    "/siembras/{siembra_id}/cancelar", response_model=SiembraSalida, summary="Cancelar una siembra"
)
async def cancelar_siembra(
    db: BD, usuario: EscribeProduccion, siembra_id: uuid.UUID
) -> SiembraSalida:
    return SiembraSalida.model_validate(await siembra_service.cancelar(db, usuario, siembra_id))


@router.get(
    "/siembras/{siembra_id}/ciclos",
    response_model=list[CicloSalida],
    summary="Ciclos de una siembra",
)
async def listar_ciclos(db: BD, usuario: LeeProduccion, siembra_id: uuid.UUID) -> list[CicloSalida]:
    siembra = await siembra_service.obtener(db, usuario, siembra_id)
    return [CicloSalida.model_validate(c) for c in siembra.ciclos]


@router.post(
    "/siembras/{siembra_id}/ciclos",
    response_model=CicloSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Abrir el siguiente ciclo",
)
async def abrir_ciclo(
    db: BD, usuario: EscribeProduccion, siembra_id: uuid.UUID, datos: CicloCrear
) -> CicloSalida:
    return CicloSalida.model_validate(
        await siembra_service.crear_ciclo(db, usuario, siembra_id, datos.tipo)
    )


@router.post(
    "/siembras/{siembra_id}/renovar",
    response_model=CicloSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Abrir el ciclo de renovación (soqueo)",
)
async def renovar(db: BD, usuario: EscribeProduccion, siembra_id: uuid.UUID) -> CicloSalida:
    return CicloSalida.model_validate(
        await siembra_service.crear_ciclo(db, usuario, siembra_id, "renovacion")
    )


@router.get(
    "/siembras/{siembra_id}/conteos",
    response_model=list[ConteoSalida],
    summary="Conteos de plantas",
)
async def listar_conteos(
    db: BD, usuario: LeeProduccion, siembra_id: uuid.UUID
) -> list[ConteoSalida]:
    return [
        ConteoSalida.model_validate(c) for c in await conteo_service.listar(db, usuario, siembra_id)
    ]


@router.post(
    "/siembras/{siembra_id}/conteos",
    response_model=ConteoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un conteo de plantas",
)
async def crear_conteo(
    db: BD, usuario: EscribeProduccion, siembra_id: uuid.UUID, datos: ConteoCrear
) -> ConteoSalida:
    return ConteoSalida.model_validate(await conteo_service.crear(db, usuario, siembra_id, datos))


@router.get(
    "/siembras/{siembra_id}/indices", response_model=IndicesSalida, summary="Índices por planta"
)
async def indices(db: BD, usuario: LeeProduccion, siembra_id: uuid.UUID) -> IndicesSalida:
    return await conteo_service.indices(db, usuario, siembra_id)


@router.get("/ciclos/{ciclo_id}", response_model=CicloSalida, summary="Detalle de un ciclo")
async def ver_ciclo(db: BD, usuario: LeeProduccion, ciclo_id: uuid.UUID) -> CicloSalida:
    ciclo, _ = await siembra_service.obtener_ciclo(db, usuario, ciclo_id)
    return CicloSalida.model_validate(ciclo)


@router.post("/ciclos/{ciclo_id}/iniciar", response_model=CicloSalida, summary="Iniciar un ciclo")
async def iniciar_ciclo(
    db: BD, usuario: EscribeProduccion, ciclo_id: uuid.UUID, datos: IniciarEntrada | None = None
) -> CicloSalida:
    fecha = datos.fecha_inicio if datos else None
    return CicloSalida.model_validate(
        await siembra_service.iniciar_ciclo(db, usuario, ciclo_id, fecha)
    )


@router.post("/ciclos/{ciclo_id}/cerrar", response_model=CicloSalida, summary="Cerrar un ciclo")
async def cerrar_ciclo(
    db: BD, usuario: EscribeProduccion, ciclo_id: uuid.UUID, datos: CerrarCicloEntrada | None = None
) -> CicloSalida:
    return CicloSalida.model_validate(
        await siembra_service.cerrar_ciclo(db, usuario, ciclo_id, datos or CerrarCicloEntrada())
    )


@router.get(
    "/ciclos/{ciclo_id}/cronograma",
    response_model=CronogramaSalida,
    summary="Cronograma planeado del ciclo",
)
async def cronograma(db: BD, usuario: LeeProduccion, ciclo_id: uuid.UUID) -> CronogramaSalida:
    return await conteo_service.cronograma(db, usuario, ciclo_id)


@router.get(
    "/ciclos/{ciclo_id}/necesidad-insumos",
    response_model=NecesidadSalida,
    summary="Cuánto insumo se necesita",
)
async def necesidad_insumos(db: BD, usuario: LeeProduccion, ciclo_id: uuid.UUID) -> NecesidadSalida:
    return await conteo_service.necesidad_insumos(db, usuario, ciclo_id)
