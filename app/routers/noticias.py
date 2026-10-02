"""Noticias por región y cultivo; todas vencen solas."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.etiquetas import NOTICIAS
from app.dependencies import Autenticado, SoloAdmin
from app.routers.dependencias import BD, Pagina, armar_pagina
from app.schemas.common import Page
from app.schemas.noticia import NoticiaCrear, NoticiaSalida
from app.services import noticia_service as servicio

router = APIRouter(tags=[NOTICIAS])


@router.get(
    "/noticias", response_model=Page[NoticiaSalida], summary="Noticias vigentes de mi región"
)
async def listar(
    db: BD,
    usuario: Autenticado,
    pag: Pagina,
    region: Annotated[
        str | None,
        Query(pattern=r"^(\d{2}|\d{5})$", description="Código DANE; por defecto, el de sus fincas"),
    ] = None,
    cultivo_id: uuid.UUID | None = None,
) -> Page[NoticiaSalida]:
    items, total = await servicio.listar(db, usuario, region, cultivo_id, pag.skip, pag.limit)
    return armar_pagina([NoticiaSalida.model_validate(n) for n in items], total, pag)


@router.post(
    "/noticias",
    response_model=NoticiaSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Cargar una noticia",
)
async def crear(db: BD, usuario: SoloAdmin, datos: NoticiaCrear) -> NoticiaSalida:
    return NoticiaSalida.model_validate(await servicio.crear(db, datos, usuario.id))
