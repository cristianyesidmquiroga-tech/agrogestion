import uuid
from collections import defaultdict
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    EtapaProceso,
    Finca,
    Insumo,
    Jornal,
    MovimientoInsumo,
    Proceso,
    Trabajador,
)
from app.schemas.estadisticas import (
    ExistenciaPorUnidad,
    InsumoConsumido,
    InventarioGeneral,
    ManoDeObraGeneral,
    ManoDeObraZona,
    ProcesoPorProducto,
    ProcesosGeneral,
    TotalPorCategoria,
)

CERO = Decimal(0)
SIN_ZONA = "sin_zona"
MAS_CONSUMIDOS = 10


async def _filas(db: AsyncSession, consulta: Any) -> list[Any]:
    return list((await db.execute(consulta)).all())


def _promedio(valores: list[int]) -> float | None:
    return sum(valores) / len(valores) if valores else None


async def _zona_de_fincas(db: AsyncSession) -> dict[uuid.UUID, str]:
    filas = await _filas(db, select(Finca.id, Finca.departamento_dane))
    return {finca_id: zona or SIN_ZONA for finca_id, zona in filas}


async def mano_de_obra(db: AsyncSession) -> ManoDeObraGeneral:
    zona_de = await _zona_de_fincas(db)
    por_tipo: dict[str, int] = defaultdict(int)
    trabajadores: dict[str, int] = defaultdict(int)
    for finca_id, tipo in await _filas(
        db, select(Trabajador.finca_id, Trabajador.tipo).where(Trabajador.estado == "activo")
    ):
        por_tipo[tipo] += 1
        trabajadores[zona_de[finca_id]] += 1

    pendientes = pagados = 0
    total_pendiente = total_pagado = CERO
    modalidades: dict[str, list[Any]] = defaultdict(lambda: [0, CERO])
    zonas: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"jornales": 0, "pendiente": CERO, "pagado": CERO}
    )
    for finca_id, estado, modalidad, total in await _filas(
        db, select(Jornal.finca_id, Jornal.estado, Jornal.modalidad, Jornal.total)
    ):
        valor = Decimal(total)
        zona = zonas[zona_de[finca_id]]
        zona["jornales"] += 1
        modalidades[modalidad][0] += 1
        modalidades[modalidad][1] += valor
        if estado == "pagado":
            pagados += 1
            total_pagado += valor
            zona["pagado"] += valor
        else:
            pendientes += 1
            total_pendiente += valor
            zona["pendiente"] += valor

    nombres_de_zona = sorted(set(zonas) | set(trabajadores))
    return ManoDeObraGeneral(
        trabajadores=sum(por_tipo.values()),
        trabajadores_por_tipo=dict(por_tipo),
        jornales=pendientes + pagados,
        jornales_pendientes=pendientes,
        total_pendiente=total_pendiente,
        jornales_pagados=pagados,
        total_pagado=total_pagado,
        por_modalidad=[
            TotalPorCategoria(categoria=m, registros=datos[0], total=datos[1])
            for m, datos in sorted(modalidades.items(), key=lambda par: (-par[1][1], par[0]))
        ],
        por_zona=[
            ManoDeObraZona(
                zona=z,
                trabajadores=trabajadores[z],
                jornales=zonas[z]["jornales"],
                pendiente=zonas[z]["pendiente"],
                pagado=zonas[z]["pagado"],
            )
            for z in nombres_de_zona
        ],
    )


async def inventario(db: AsyncSession) -> InventarioGeneral:
    activos = Insumo.estado == "activo"
    por_unidad = await _filas(
        db,
        select(Insumo.unidad, func.count(), func.coalesce(func.sum(Insumo.existencia), 0))
        .where(activos)
        .group_by(Insumo.unidad)
        .order_by(Insumo.unidad),
    )
    agotados = await db.scalar(
        select(func.count()).select_from(Insumo).where(activos, Insumo.existencia <= 0)
    )
    entradas = (
        await db.execute(
            select(func.count(), func.coalesce(func.sum(MovimientoInsumo.costo), 0)).where(
                MovimientoInsumo.tipo == "entrada"
            )
        )
    ).one()
    consumos = await db.scalar(
        select(func.count()).select_from(MovimientoInsumo).where(MovimientoInsumo.tipo == "consumo")
    )
    consumido = func.coalesce(func.sum(MovimientoInsumo.cantidad), 0)
    ranking = await _filas(
        db,
        select(Insumo.nombre, Insumo.unidad, consumido)
        .join(MovimientoInsumo, MovimientoInsumo.insumo_id == Insumo.id)
        .where(MovimientoInsumo.tipo == "consumo")
        .group_by(Insumo.nombre, Insumo.unidad)
        .order_by(consumido.desc(), Insumo.nombre)
        .limit(MAS_CONSUMIDOS),
    )
    return InventarioGeneral(
        insumos=sum(int(n) for _, n, _ in por_unidad),
        agotados=int(agotados or 0),
        entradas=int(entradas[0]),
        costo_entradas=Decimal(entradas[1]),
        consumos=int(consumos or 0),
        por_unidad=[
            ExistenciaPorUnidad(unidad=u, insumos=int(n), existencia=Decimal(e))
            for u, n, e in por_unidad
        ],
        mas_consumidos=[
            InsumoConsumido(nombre=nombre, unidad=unidad, consumido=Decimal(cantidad))
            for nombre, unidad, cantidad in ranking
        ],
    )


async def procesos(db: AsyncSession) -> ProcesosGeneral:
    por_origen: dict[str, int] = defaultdict(int)
    duraciones: list[int] = []
    por_producto: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"procesos": 0, "finalizados": 0, "duraciones": []}
    )
    for producto, origen, inicio, fin in await _filas(
        db,
        select(Proceso.producto, Proceso.origen_materia, Proceso.fecha_inicio, Proceso.fecha_fin),
    ):
        por_origen[origen] += 1
        datos = por_producto[producto]
        datos["procesos"] += 1
        if fin is not None:
            dias = (fin.date() - inicio.date()).days
            duraciones.append(dias)
            datos["finalizados"] += 1
            datos["duraciones"].append(dias)

    etapas = finalizadas = retrasadas = 0
    for dias_estimados, inicio, fin in await _filas(
        db,
        select(EtapaProceso.dias_estimados, EtapaProceso.iniciado_en, EtapaProceso.finalizado_en),
    ):
        etapas += 1
        if fin is not None:
            finalizadas += 1
            if (
                inicio is not None
                and (fin - inicio).total_seconds() > float(dias_estimados) * 86400
            ):
                retrasadas += 1

    total = sum(por_origen.values())
    return ProcesosGeneral(
        procesos=total,
        en_curso=total - len(duraciones),
        finalizados=len(duraciones),
        duracion_media_dias=_promedio(duraciones),
        por_origen=dict(por_origen),
        etapas=etapas,
        etapas_finalizadas=finalizadas,
        etapas_con_retraso=retrasadas,
        por_producto=[
            ProcesoPorProducto(
                producto=p,
                procesos=d["procesos"],
                finalizados=d["finalizados"],
                duracion_media_dias=_promedio(d["duraciones"]),
            )
            for p, d in sorted(por_producto.items(), key=lambda par: (-par[1]["procesos"], par[0]))
        ],
    )
