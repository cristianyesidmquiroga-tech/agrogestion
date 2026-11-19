import uuid
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ciclo, Cosecha, Cultivo, Finca, Siembra, Usuario
from app.schemas.estadisticas import (
    CantidadPorUnidad,
    CosechaRegistrada,
    Productor,
    SiembraRegistrada,
)

SIN_ZONA = "sin_zona"


def _de_la_zona(zona: str | None) -> list[Any]:
    if not zona:
        return []
    columna = Finca.departamento_dane if len(zona) == 2 else Finca.municipio_dane
    return [columna == zona]


def _zona(finca: Finca) -> str:
    return finca.municipio_dane or finca.departamento_dane or SIN_ZONA


async def producciones(
    db: AsyncSession,
    cultivo_id: uuid.UUID | None,
    zona: str | None,
    desde: date | None,
    hasta: date | None,
    skip: int,
    limit: int,
) -> tuple[list[CosechaRegistrada], int]:
    consulta = (
        select(Cosecha, Cultivo.nombre, Finca, Usuario.nombre)
        .join(Ciclo, Ciclo.id == Cosecha.ciclo_id)
        .join(Siembra, Siembra.id == Ciclo.siembra_id)
        .join(Cultivo, Cultivo.id == Siembra.cultivo_id)
        .join(Finca, Finca.id == Cosecha.finca_id)
        .outerjoin(Usuario, Usuario.id == Cosecha.creado_por)
        .where(Cosecha.estado == "activa", *_de_la_zona(zona))
    )
    if cultivo_id:
        consulta = consulta.where(Siembra.cultivo_id == cultivo_id)
    if desde:
        consulta = consulta.where(func.date(Cosecha.fecha) >= desde)
    if hasta:
        consulta = consulta.where(func.date(Cosecha.fecha) <= hasta)
    total = await db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    filas = (
        await db.execute(
            consulta.order_by(Cosecha.fecha.desc(), Cosecha.id).offset(skip).limit(limit)
        )
    ).all()
    items = [
        CosechaRegistrada(
            id=c.id,
            fecha=c.fecha.date(),
            cultivo=cultivo,
            cantidad=c.cantidad,
            unidad=c.unidad,
            calidad=c.calidad,
            finca=finca.nombre,
            zona=_zona(finca),
            agricultor=agricultor,
        )
        for c, cultivo, finca, agricultor in filas
    ]
    return items, int(total)


async def siembras(
    db: AsyncSession,
    cultivo_id: uuid.UUID | None,
    estado: str | None,
    zona: str | None,
    skip: int,
    limit: int,
) -> tuple[list[SiembraRegistrada], int]:
    consulta = (
        select(Siembra, Cultivo.nombre, Finca, Usuario.nombre)
        .join(Cultivo, Cultivo.id == Siembra.cultivo_id)
        .join(Finca, Finca.id == Siembra.finca_id)
        .outerjoin(Usuario, Usuario.id == Siembra.creado_por)
        .where(*_de_la_zona(zona))
    )
    if cultivo_id:
        consulta = consulta.where(Siembra.cultivo_id == cultivo_id)
    if estado:
        consulta = consulta.where(Siembra.estado == estado)
    total = await db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    filas = (
        await db.execute(
            consulta.order_by(Siembra.fecha_plan.desc(), Siembra.id).offset(skip).limit(limit)
        )
    ).all()
    inicios = {
        siembra_id: inicio
        for siembra_id, inicio in (
            await db.execute(
                select(Ciclo.siembra_id, func.min(Ciclo.fecha_inicio))
                .where(Ciclo.siembra_id.in_([s.id for s, *_ in filas]))
                .group_by(Ciclo.siembra_id)
            )
        ).all()
    }
    items = [
        SiembraRegistrada(
            id=s.id,
            cultivo=cultivo,
            estado=s.estado,
            area_ha=s.area_ha,
            plantas=s.plantas_sembradas,
            fecha_plan=s.fecha_plan,
            inicio_ciclo=inicios[s.id].date() if inicios.get(s.id) else None,
            finca=finca.nombre,
            zona=_zona(finca),
            agricultor=agricultor,
        )
        for s, cultivo, finca, agricultor in filas
    ]
    return items, int(total)


async def productores(db: AsyncSession) -> list[Productor]:
    filas = (
        await db.execute(
            select(
                Cosecha.creado_por,
                Usuario.nombre,
                Cosecha.finca_id,
                Cosecha.fecha,
                Cosecha.cantidad,
                Cosecha.unidad,
            )
            .join(Usuario, Usuario.id == Cosecha.creado_por)
            .where(Cosecha.estado == "activa")
        )
    ).all()
    nombres: dict[uuid.UUID, str] = {}
    fincas: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
    cosechas: dict[uuid.UUID, int] = defaultdict(int)
    ultima: dict[uuid.UUID, date] = {}
    produccion: dict[uuid.UUID, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    for usuario_id, nombre, finca_id, fecha, cantidad, unidad in filas:
        nombres[usuario_id] = nombre
        fincas[usuario_id].add(finca_id)
        cosechas[usuario_id] += 1
        produccion[usuario_id][unidad] += Decimal(cantidad)
        ultima[usuario_id] = max(ultima.get(usuario_id, fecha.date()), fecha.date())
    ranking = [
        Productor(
            usuario_id=usuario_id,
            nombre=nombre,
            fincas=len(fincas[usuario_id]),
            cosechas=cosechas[usuario_id],
            produccion=[
                CantidadPorUnidad(unidad=u, cantidad=c)
                for u, c in sorted(produccion[usuario_id].items())
            ],
            ultima_cosecha=ultima[usuario_id],
        )
        for usuario_id, nombre in nombres.items()
    ]
    return sorted(ranking, key=lambda p: (-p.cosechas, p.nombre))
