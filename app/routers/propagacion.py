"""Vivero: propagación por semilla, esqueje u otros métodos."""

import uuid

from fastapi import APIRouter, status

from app.core.security import EscribeProduccion
from app.routers.dependencias import BD, Pagina, armar_pagina
from app.schemas.common import Page
from app.schemas.propagacion import (
    PropagacionActualizar,
    PropagacionCrear,
    PropagacionSalida,
    TrasplanteEntrada,
)
from app.services import propagacion_service

router = APIRouter(prefix="/propagacion", tags=["propagacion"])


@router.get("", response_model=Page[PropagacionSalida], summary="Lotes de vivero")
async def listar(
    db: BD, usuario: EscribeProduccion, pag: Pagina, pendientes: bool | None = None
) -> Page[PropagacionSalida]:
    items, total = await propagacion_service.listar(db, usuario, pendientes, pag.skip, pag.limit)
    return armar_pagina([PropagacionSalida.model_validate(i) for i in items], total, pag)


@router.post(
    "",
    response_model=PropagacionSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un lote de vivero",
)
async def crear(db: BD, usuario: EscribeProduccion, datos: PropagacionCrear) -> PropagacionSalida:
    return PropagacionSalida.model_validate(await propagacion_service.crear(db, usuario, datos))


@router.patch(
    "/{lote_id}",
    response_model=PropagacionSalida,
    summary="Actualizar germinadas, listas y pérdidas",
)
async def actualizar(
    db: BD, usuario: EscribeProduccion, lote_id: uuid.UUID, datos: PropagacionActualizar
) -> PropagacionSalida:
    return PropagacionSalida.model_validate(
        await propagacion_service.actualizar(db, usuario, lote_id, datos)
    )


@router.post(
    "/{lote_id}/trasplante",
    response_model=PropagacionSalida,
    summary="Pasar plantas listas a una siembra",
)
async def trasplantar(
    db: BD, usuario: EscribeProduccion, lote_id: uuid.UUID, datos: TrasplanteEntrada
) -> PropagacionSalida:
    return PropagacionSalida.model_validate(
        await propagacion_service.trasplantar(db, usuario, lote_id, datos)
    )
