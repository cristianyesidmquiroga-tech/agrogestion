"""Eventos adversos: heladas, sequías, granizo, plagas y otros."""

import uuid

from fastapi import APIRouter, status

from app.core.catalogos import TipoRiesgo
from app.core.security import EscribeProduccion
from app.routers.dependencias import BD, Pagina, armar_pagina
from app.schemas.common import Page
from app.schemas.evento import EventoActualizar, EventoCrear, EventoSalida
from app.services import evento_service

router = APIRouter(prefix="/eventos-adversos", tags=["eventos"])


@router.get("", response_model=Page[EventoSalida], summary="Eventos adversos")
async def listar(
    db: BD,
    usuario: EscribeProduccion,
    pag: Pagina,
    tipo: TipoRiesgo | None = None,
    finca_id: uuid.UUID | None = None,
) -> Page[EventoSalida]:
    items, total = await evento_service.listar(db, usuario, tipo, finca_id, pag.skip, pag.limit)
    return armar_pagina([EventoSalida.model_validate(e) for e in items], total, pag)


@router.post(
    "",
    response_model=EventoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un evento adverso",
)
async def crear(db: BD, usuario: EscribeProduccion, datos: EventoCrear) -> EventoSalida:
    return EventoSalida.model_validate(await evento_service.crear(db, usuario, datos))


@router.get("/{evento_id}", response_model=EventoSalida, summary="Detalle de un evento")
async def ver(db: BD, usuario: EscribeProduccion, evento_id: uuid.UUID) -> EventoSalida:
    return EventoSalida.model_validate(await evento_service.obtener(db, usuario, evento_id))


@router.patch("/{evento_id}", response_model=EventoSalida, summary="Actualizar un evento")
async def actualizar(
    db: BD, usuario: EscribeProduccion, evento_id: uuid.UUID, datos: EventoActualizar
) -> EventoSalida:
    return EventoSalida.model_validate(
        await evento_service.actualizar(db, usuario, evento_id, datos)
    )
