"""Glosario, política de datos y consentimiento."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.security import Autenticado
from app.routers.dependencias import BD
from app.schemas.cuenta import (
    ConsentimientoEntrada,
    ConsentimientoSalida,
    PoliticaSalida,
    TerminoSalida,
)
from app.services import cuenta_service

router = APIRouter(tags=["cuenta"])


@router.get("/glosario", response_model=list[TerminoSalida], summary="Términos del agro explicados")
async def glosario(
    db: BD,
    _: Autenticado,
    q: Annotated[str | None, Query(max_length=60, description="Término a buscar")] = None,
) -> list[TerminoSalida]:
    return [TerminoSalida.model_validate(t) for t in await cuenta_service.glosario(db, q)]


@router.get("/politica", response_model=PoliticaSalida, summary="Política de tratamiento de datos")
async def politica() -> PoliticaSalida:
    return cuenta_service.politica()


@router.get(
    "/cuenta/consentimiento",
    response_model=ConsentimientoSalida,
    summary="Última autorización aceptada",
)
async def ver_consentimiento(db: BD, usuario: Autenticado) -> ConsentimientoSalida:
    return ConsentimientoSalida.model_validate(await cuenta_service.ultimo(db, usuario.id))


@router.post(
    "/cuenta/consentimiento",
    response_model=ConsentimientoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Aceptar el tratamiento de datos",
)
async def aceptar(
    db: BD, usuario: Autenticado, datos: ConsentimientoEntrada
) -> ConsentimientoSalida:
    return ConsentimientoSalida.model_validate(
        await cuenta_service.registrar(db, usuario.id, datos)
    )
