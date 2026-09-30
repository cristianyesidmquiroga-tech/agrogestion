"""Base de conocimiento: todos leen lo validado; los expertos crean y revisan."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.catalogos import EstadoConocimiento, TipoProblema
from app.core.security import Autenticado, Revisa
from app.routers.dependencias import BD, Pagina, armar_pagina
from app.schemas.common import Page
from app.schemas.conocimiento import (
    CambiarEstado,
    FuenteCrear,
    FuenteSalida,
    ProblemaCrear,
    ProblemaResumen,
    ProblemaRevision,
)
from app.services import conocimiento_service as servicio

router = APIRouter(tags=["conocimiento"])


def _ficha(problema: object, revisa: bool) -> ProblemaRevision:
    ficha = ProblemaRevision.model_validate(problema)
    return ficha if revisa else ficha.model_copy(update={"validaciones": []})


@router.get(
    "/conocimiento", response_model=Page[ProblemaResumen], summary="Buscar en la biblioteca"
)
async def listar(
    db: BD,
    usuario: Autenticado,
    pag: Pagina,
    q: Annotated[
        str | None, Query(max_length=80, description="Texto en el nombre o los síntomas")
    ] = None,
    cultivo_id: uuid.UUID | None = None,
    tipo: TipoProblema | None = None,
    estado: Annotated[
        EstadoConocimiento | None, Query(description="Solo lo usan administradores y expertos")
    ] = None,
) -> Page[ProblemaResumen]:
    items, total = await servicio.listar(
        db, usuario, q, cultivo_id, tipo, estado, pag.skip, pag.limit
    )
    return armar_pagina([ProblemaResumen.model_validate(i) for i in items], total, pag)


@router.post(
    "/conocimiento",
    response_model=ProblemaRevision,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una ficha en borrador",
)
async def crear(db: BD, usuario: Revisa, datos: ProblemaCrear) -> ProblemaRevision:
    return _ficha(await servicio.crear(db, datos, usuario.id), True)


@router.get(
    "/conocimiento/{problema_id}", response_model=ProblemaRevision, summary="Ficha de un problema"
)
async def ver(db: BD, usuario: Autenticado, problema_id: uuid.UUID) -> ProblemaRevision:
    problema = await servicio.obtener(db, usuario, problema_id)
    return _ficha(problema, usuario.rol in servicio.REVISORES)


@router.patch(
    "/conocimiento/{problema_id}/estado",
    response_model=ProblemaRevision,
    summary="Validar, retirar o reabrir una ficha",
)
async def cambiar_estado(
    db: BD, usuario: Revisa, problema_id: uuid.UUID, datos: CambiarEstado
) -> ProblemaRevision:
    return _ficha(await servicio.cambiar_estado(db, problema_id, datos, usuario.id), True)


@router.get("/fuentes", response_model=list[FuenteSalida], summary="Fuentes de la biblioteca")
async def listar_fuentes(db: BD, _: Revisa) -> list[FuenteSalida]:
    return [FuenteSalida.model_validate(f) for f in await servicio.listar_fuentes(db)]


@router.post(
    "/fuentes",
    response_model=FuenteSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar una fuente",
)
async def crear_fuente(db: BD, usuario: Revisa, datos: FuenteCrear) -> FuenteSalida:
    return FuenteSalida.model_validate(await servicio.crear_fuente(db, datos, usuario.id))
