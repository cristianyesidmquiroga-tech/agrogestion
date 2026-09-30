"""Catálogo de cultivos con su perfil y el catálogo de riesgos."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.catalogos import TipoCiclo
from app.core.security import EscribeProduccion, SoloAdmin
from app.routers.dependencias import BD, Pagina, armar_pagina
from app.schemas.common import Page
from app.schemas.cultivo import (
    CultivoActualizar,
    CultivoCrear,
    CultivoResumen,
    CultivoRiesgoEntrada,
    CultivoRiesgoSalida,
    CultivoSalida,
    DosisSalida,
    FaseSalida,
    MetodoSalida,
    RiesgoCrear,
    RiesgoSalida,
)
from app.services import cultivo_service

router = APIRouter(tags=["cultivos"])


@router.get("/cultivos", response_model=Page[CultivoResumen], summary="Buscar cultivos")
async def listar_cultivos(
    db: BD,
    _: EscribeProduccion,
    pag: Pagina,
    q: Annotated[
        str | None, Query(max_length=80, description="Texto a buscar en el nombre")
    ] = None,
    tipo_ciclo: TipoCiclo | None = None,
) -> Page[CultivoResumen]:
    items, total = await cultivo_service.listar(db, q, tipo_ciclo, pag.skip, pag.limit)
    return armar_pagina([CultivoResumen.model_validate(c) for c in items], total, pag)


@router.post(
    "/cultivos",
    response_model=CultivoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un cultivo con su perfil",
)
async def crear_cultivo(db: BD, usuario: EscribeProduccion, datos: CultivoCrear) -> CultivoSalida:
    return CultivoSalida.model_validate(await cultivo_service.crear(db, datos, usuario.id))


@router.get(
    "/cultivos/{cultivo_id}", response_model=CultivoSalida, summary="Ver el perfil de un cultivo"
)
async def ver_cultivo(db: BD, _: EscribeProduccion, cultivo_id: uuid.UUID) -> CultivoSalida:
    return CultivoSalida.model_validate(await cultivo_service.obtener(db, cultivo_id))


@router.put(
    "/cultivos/{cultivo_id}",
    response_model=CultivoSalida,
    summary="Reemplazar el perfil de un cultivo",
)
async def actualizar_cultivo(
    db: BD, _: EscribeProduccion, cultivo_id: uuid.UUID, datos: CultivoActualizar
) -> CultivoSalida:
    return CultivoSalida.model_validate(await cultivo_service.actualizar(db, cultivo_id, datos))


@router.get(
    "/cultivos/{cultivo_id}/fases", response_model=list[FaseSalida], summary="Fases del cultivo"
)
async def fases(db: BD, _: EscribeProduccion, cultivo_id: uuid.UUID) -> list[FaseSalida]:
    cultivo = await cultivo_service.obtener(db, cultivo_id)
    return [FaseSalida.model_validate(f) for f in cultivo.fases]


@router.get(
    "/cultivos/{cultivo_id}/metodos",
    response_model=list[MetodoSalida],
    summary="Métodos de propagación",
)
async def metodos(db: BD, _: EscribeProduccion, cultivo_id: uuid.UUID) -> list[MetodoSalida]:
    cultivo = await cultivo_service.obtener(db, cultivo_id)
    return [MetodoSalida.model_validate(m) for m in cultivo.metodos]


@router.get(
    "/cultivos/{cultivo_id}/dosis", response_model=list[DosisSalida], summary="Dosis de referencia"
)
async def dosis(db: BD, _: EscribeProduccion, cultivo_id: uuid.UUID) -> list[DosisSalida]:
    cultivo = await cultivo_service.obtener(db, cultivo_id)
    return [DosisSalida.model_validate(d) for d in cultivo.dosis]


@router.get(
    "/cultivos/{cultivo_id}/riesgos",
    response_model=list[CultivoRiesgoSalida],
    summary="Riesgos del cultivo",
)
async def riesgos_cultivo(
    db: BD, _: EscribeProduccion, cultivo_id: uuid.UUID
) -> list[CultivoRiesgoSalida]:
    filas = await cultivo_service.riesgos_del_cultivo(db, cultivo_id)
    return [CultivoRiesgoSalida.model_validate(r) for r in filas]


@router.put(
    "/cultivos/{cultivo_id}/riesgos",
    response_model=list[CultivoRiesgoSalida],
    summary="Reemplazar los riesgos del cultivo",
)
async def reemplazar_riesgos_cultivo(
    db: BD, _: EscribeProduccion, cultivo_id: uuid.UUID, datos: list[CultivoRiesgoEntrada]
) -> list[CultivoRiesgoSalida]:
    filas = await cultivo_service.reemplazar_riesgos(db, cultivo_id, datos)
    return [CultivoRiesgoSalida.model_validate(r) for r in filas]


@router.get("/riesgos", response_model=list[RiesgoSalida], summary="Catálogo de riesgos")
async def listar_riesgos(db: BD, _: EscribeProduccion) -> list[RiesgoSalida]:
    return [RiesgoSalida.model_validate(r) for r in await cultivo_service.listar_riesgos(db)]


@router.post(
    "/riesgos",
    response_model=RiesgoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar un riesgo al catálogo",
)
async def crear_riesgo(db: BD, usuario: SoloAdmin, datos: RiesgoCrear) -> RiesgoSalida:
    return RiesgoSalida.model_validate(await cultivo_service.crear_riesgo(db, datos, usuario.id))
