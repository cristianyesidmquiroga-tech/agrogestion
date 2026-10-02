"""Asistente de consultas sobre la base de conocimiento validada."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.etiquetas import ASISTENTE
from app.dependencies import EscribeProduccion, SoloAdmin
from app.routers.dependencias import BD, Pagina, armar_pagina
from app.schemas.asistente import (
    CalidadSalida,
    ConsultaCrear,
    ConsultaResumen,
    ConsultaSalida,
    RetroalimentacionEntrada,
    RetroalimentacionSalida,
)
from app.schemas.common import ErrorRespuesta, Page
from app.services import asistente_service as servicio

router = APIRouter(tags=[ASISTENTE])


@router.post(
    "/consultas",
    response_model=ConsultaSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Preguntarle al asistente",
    responses={
        429: {"model": ErrorRespuesta, "description": "Llegó al máximo de consultas del día."}
    },
)
async def preguntar(db: BD, usuario: EscribeProduccion, datos: ConsultaCrear) -> ConsultaSalida:
    return await servicio.crear(db, usuario, datos)


@router.get("/consultas", response_model=Page[ConsultaResumen], summary="Historial de consultas")
async def historial(
    db: BD,
    usuario: EscribeProduccion,
    pag: Pagina,
    q: Annotated[str | None, Query(max_length=80, description="Texto en la pregunta")] = None,
) -> Page[ConsultaResumen]:
    items, total = await servicio.listar(db, usuario, q, pag.skip, pag.limit)
    return armar_pagina(items, total, pag)


@router.get(
    "/consultas/{consulta_id}", response_model=ConsultaSalida, summary="Una consulta y su respuesta"
)
async def ver(db: BD, usuario: EscribeProduccion, consulta_id: uuid.UUID) -> ConsultaSalida:
    return await servicio.obtener(db, usuario, consulta_id)


@router.post(
    "/consultas/{consulta_id}/retroalimentacion",
    response_model=RetroalimentacionSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Decir si la respuesta sirvió",
)
async def valorar(
    db: BD, usuario: EscribeProduccion, consulta_id: uuid.UUID, datos: RetroalimentacionEntrada
) -> RetroalimentacionSalida:
    fila = await servicio.valorar(db, usuario, consulta_id, datos)
    return RetroalimentacionSalida.model_validate(fila)


@router.get("/asistente/calidad", response_model=CalidadSalida, summary="Calidad del asistente")
async def calidad(db: BD, _: SoloAdmin) -> CalidadSalida:
    return await servicio.calidad(db)
