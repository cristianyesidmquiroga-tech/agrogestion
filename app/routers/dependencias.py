"""Piezas comunes de los routers: base de datos y paginación."""

from dataclasses import dataclass
from typing import Annotated, TypeVar

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import Page

T = TypeVar("T")

BD = Annotated[AsyncSession, Depends(get_db)]


@dataclass(frozen=True)
class Paginacion:
    skip: int
    limit: int


def paginacion(
    skip: Annotated[int, Query(ge=0, description="Registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=50, description="Tamaño de página, máximo 50")] = 10,
) -> Paginacion:
    return Paginacion(skip=skip, limit=limit)


Pagina = Annotated[Paginacion, Depends(paginacion)]


def armar_pagina(items: list[T], total: int, pag: Paginacion) -> Page[T]:
    return Page[T](
        items=items,
        total=total,
        page=pag.skip // pag.limit + 1,
        size=pag.limit,
        has_more=pag.skip + len(items) < total,
    )
