from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Actividad,
    EtapaProceso,
    Insumo,
    Jornal,
    MovimientoInsumo,
    Proceso,
    Trabajador,
)
from app.services.lands import user_finca


async def list_jornales(
    db: AsyncSession, user_id: UUID, finca_id: UUID, estado: str | None = None
) -> list[dict[str, Any]]:
    await user_finca(db, user_id, finca_id)
    query = (
        select(Jornal, Trabajador.nombre, Actividad.nombre)
        .outerjoin(Trabajador, Trabajador.id == Jornal.trabajador_id)
        .join(Actividad, Actividad.id == Jornal.actividad_id)
        .where(Jornal.finca_id == finca_id)
        .order_by(Jornal.fecha.desc())
    )
    if estado:
        query = query.where(Jornal.estado == estado)
    filas = (await db.execute(query)).all()
    return [
        {
            **{c: getattr(j, c) for c in _CAMPOS_JORNAL},
            "trabajador_nombre": trabajador,
            "actividad_nombre": actividad,
        }
        for j, trabajador, actividad in filas
    ]


_CAMPOS_JORNAL = (
    "id",
    "trabajador_id",
    "actividad_id",
    "ciclo_id",
    "fecha",
    "obreros",
    "dias",
    "valor_jornal",
    "modalidad",
    "total",
    "estado",
    "pagado_en",
)


async def list_insumos(db: AsyncSession, user_id: UUID, finca_id: UUID) -> list[dict[str, Any]]:
    await user_finca(db, user_id, finca_id)
    insumos = list(
        await db.scalars(select(Insumo).where(Insumo.finca_id == finca_id).order_by(Insumo.nombre))
    )
    entradas = {
        insumo_id: (cantidad, costo)
        for insumo_id, cantidad, costo in (
            await db.execute(
                select(
                    MovimientoInsumo.insumo_id,
                    func.sum(MovimientoInsumo.cantidad),
                    func.sum(MovimientoInsumo.costo),
                )
                .where(MovimientoInsumo.finca_id == finca_id, MovimientoInsumo.tipo == "entrada")
                .group_by(MovimientoInsumo.insumo_id)
            )
        ).all()
    }
    filas_ultimo = await db.execute(
        select(MovimientoInsumo.insumo_id, func.max(MovimientoInsumo.fecha))
        .where(MovimientoInsumo.finca_id == finca_id)
        .group_by(MovimientoInsumo.insumo_id)
    )
    ultimos: dict[UUID, datetime] = {insumo_id: fecha for insumo_id, fecha in filas_ultimo.all()}
    salida = []
    for insumo in insumos:
        cantidad, costo = entradas.get(insumo.id, (Decimal(0), Decimal(0)))
        promedio = (costo / cantidad).quantize(Decimal("0.01")) if cantidad and costo else None
        salida.append(
            {
                "id": insumo.id,
                "nombre": insumo.nombre,
                "unidad": insumo.unidad,
                "existencia": insumo.existencia,
                "costo_promedio": promedio,
                "valor": (promedio or Decimal(0)) * insumo.existencia,
                "ultimo_movimiento": ultimos.get(insumo.id),
                "estado": insumo.estado,
            }
        )
    return salida


async def list_procesos(db: AsyncSession, user_id: UUID, finca_id: UUID) -> list[dict[str, Any]]:
    await user_finca(db, user_id, finca_id)
    procesos = list(
        await db.scalars(
            select(Proceso)
            .where(Proceso.finca_id == finca_id)
            .order_by(Proceso.fecha_inicio.desc())
        )
    )
    conteos = {
        proceso_id: (total, hechas or 0)
        for proceso_id, total, hechas in (
            await db.execute(
                select(
                    EtapaProceso.proceso_id,
                    func.count(EtapaProceso.id),
                    func.sum(case((EtapaProceso.estado == "finalizada", 1), else_=0)),
                )
                .where(EtapaProceso.finca_id == finca_id)
                .group_by(EtapaProceso.proceso_id)
            )
        ).all()
    }
    salida = []
    for p in procesos:
        total, hechas = conteos.get(p.id, (0, 0))
        salida.append(
            {
                "id": p.id,
                "nombre": p.nombre,
                "producto": p.producto,
                "materia_prima": p.materia_prima,
                "origen_materia": p.origen_materia,
                "fecha_inicio": p.fecha_inicio,
                "fecha_fin": p.fecha_fin,
                "etapas": total,
                "etapas_finalizadas": int(hechas),
                "estado": "terminado" if p.fecha_fin else "en_proceso",
            }
        )
    return salida


async def list_etapas(
    db: AsyncSession, user_id: UUID, finca_id: UUID, proceso_id: UUID
) -> list[EtapaProceso]:
    await user_finca(db, user_id, finca_id)
    resultado = await db.scalars(
        select(EtapaProceso)
        .where(EtapaProceso.finca_id == finca_id, EtapaProceso.proceso_id == proceso_id)
        .order_by(EtapaProceso.creado_en)
    )
    return list(resultado)
