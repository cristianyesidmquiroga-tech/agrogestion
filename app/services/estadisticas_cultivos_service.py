import uuid
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ciclo, Cosecha, Cultivo, Finca, FincaUsuario, Gasto, Ingreso, Siembra
from app.schemas.estadisticas import CantidadPorUnidad, EstadisticaCultivo, EstadisticaZona

CERO = Decimal(0)
SIN_ZONA = "sin_zona"


def _dias(inicio: datetime, fin: datetime) -> int:
    return (fin.date() - inicio.date()).days


def _promedio(valores: list[int]) -> float | None:
    return sum(valores) / len(valores) if valores else None


def _por_unidad(cantidades: dict[str, Decimal]) -> list[CantidadPorUnidad]:
    return [CantidadPorUnidad(unidad=u, cantidad=c) for u, c in sorted(cantidades.items())]


def _intervalos(fechas: list[date]) -> list[int]:
    orden = sorted(fechas)
    return [(b - a).days for a, b in zip(orden, orden[1:], strict=False)]


async def _filas(db: AsyncSession, consulta: Any) -> list[Any]:
    return list((await db.execute(consulta)).all())


async def cultivos(db: AsyncSession) -> list[EstadisticaCultivo]:
    base = await _filas(
        db,
        select(
            Siembra.cultivo_id,
            func.count(),
            func.count(func.distinct(Siembra.finca_id)),
            func.coalesce(func.sum(Siembra.area_ha), 0),
            func.coalesce(func.sum(Siembra.plantas_sembradas), 0),
        ).group_by(Siembra.cultivo_id),
    )
    agricultores = dict(
        await _filas(
            db,
            select(Siembra.cultivo_id, func.count(func.distinct(FincaUsuario.usuario_id)))
            .join(FincaUsuario, FincaUsuario.finca_id == Siembra.finca_id)
            .group_by(Siembra.cultivo_id),
        )
    )
    nombres = {c.id: c for c in await db.scalars(select(Cultivo))}

    abiertos: dict[uuid.UUID, int] = defaultdict(int)
    cerrados: dict[uuid.UUID, int] = defaultdict(int)
    duraciones: dict[uuid.UUID, list[int]] = defaultdict(list)
    for cultivo_id, estado, inicio, fin in await _filas(
        db,
        select(Siembra.cultivo_id, Ciclo.estado, Ciclo.fecha_inicio, Ciclo.fecha_fin).join(
            Siembra, Siembra.id == Ciclo.siembra_id
        ),
    ):
        if estado == "abierto":
            abiertos[cultivo_id] += 1
        elif estado == "cerrado":
            cerrados[cultivo_id] += 1
            if inicio and fin:
                duraciones[cultivo_id].append(_dias(inicio, fin))

    cantidad: dict[uuid.UUID, int] = defaultdict(int)
    produccion: dict[uuid.UUID, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    fechas: dict[uuid.UUID, list[date]] = defaultdict(list)
    intervalos: dict[uuid.UUID, list[int]] = defaultdict(list)
    por_ciclo: dict[tuple[uuid.UUID, uuid.UUID], list[date]] = defaultdict(list)
    for cultivo_id, ciclo_id, fecha, kilos, unidad in await _filas(
        db,
        select(
            Siembra.cultivo_id, Cosecha.ciclo_id, Cosecha.fecha, Cosecha.cantidad, Cosecha.unidad
        )
        .join(Ciclo, Ciclo.id == Cosecha.ciclo_id)
        .join(Siembra, Siembra.id == Ciclo.siembra_id)
        .where(Cosecha.estado == "activa"),
    ):
        cantidad[cultivo_id] += 1
        produccion[cultivo_id][unidad] += Decimal(kilos)
        fechas[cultivo_id].append(fecha.date())
        por_ciclo[(cultivo_id, ciclo_id)].append(fecha.date())
    for (cultivo_id, _), fechas_ciclo in por_ciclo.items():
        intervalos[cultivo_id].extend(_intervalos(fechas_ciclo))

    dinero: dict[str, dict[uuid.UUID, Decimal]] = {}
    for clave, modelo, valor in (
        ("gastos", Gasto, Gasto.monto),
        ("ingresos", Ingreso, Ingreso.total),
    ):
        dinero[clave] = {
            cultivo_id: Decimal(total)
            for cultivo_id, total in await _filas(
                db,
                select(Siembra.cultivo_id, func.coalesce(func.sum(valor), 0))
                .join(Ciclo, Ciclo.siembra_id == Siembra.id)
                .join(modelo, modelo.ciclo_id == Ciclo.id)
                .where(modelo.estado == "activo")
                .group_by(Siembra.cultivo_id),
            )
        }

    salida = []
    for cultivo_id, siembras, fincas, area, plantas in base:
        cultivo = nombres[cultivo_id]
        gastos = dinero["gastos"].get(cultivo_id, CERO)
        ingresos = dinero["ingresos"].get(cultivo_id, CERO)
        dias = duraciones[cultivo_id]
        salida.append(
            EstadisticaCultivo(
                cultivo_id=cultivo_id,
                cultivo=cultivo.nombre,
                grupo=cultivo.grupo,
                siembras=int(siembras),
                fincas=int(fincas),
                agricultores=int(agricultores.get(cultivo_id, 0)),
                area_ha=Decimal(area),
                plantas=int(plantas),
                ciclos_abiertos=abiertos[cultivo_id],
                ciclos_cerrados=cerrados[cultivo_id],
                duracion_media_dias=_promedio(dias),
                ciclo_mas_largo_dias=max(dias) if dias else None,
                cosechas=cantidad[cultivo_id],
                produccion=_por_unidad(produccion[cultivo_id]),
                primera_cosecha=min(fechas[cultivo_id]) if fechas[cultivo_id] else None,
                ultima_cosecha=max(fechas[cultivo_id]) if fechas[cultivo_id] else None,
                dias_entre_cosechas=_promedio(intervalos[cultivo_id]),
                gastos=gastos,
                ingresos=ingresos,
                utilidad=ingresos - gastos,
            )
        )
    return sorted(salida, key=lambda c: (-c.siembras, c.cultivo))


async def zonas(
    db: AsyncSession, nivel: Literal["departamento", "municipio"]
) -> list[EstadisticaZona]:
    columna = Finca.departamento_dane if nivel == "departamento" else Finca.municipio_dane
    zona_de: dict[uuid.UUID, str] = {
        finca_id: zona or SIN_ZONA for finca_id, zona in await _filas(db, select(Finca.id, columna))
    }

    def sumar(filas: list[Any]) -> dict[str, Decimal]:
        total: dict[str, Decimal] = defaultdict(Decimal)
        for finca_id, valor in filas:
            total[zona_de[finca_id]] += Decimal(valor)
        return total

    fincas: dict[str, int] = defaultdict(int)
    area_fincas: dict[str, Decimal] = defaultdict(Decimal)
    for finca_id, area in await _filas(db, select(Finca.id, func.coalesce(Finca.area_ha, 0))):
        fincas[zona_de[finca_id]] += 1
        area_fincas[zona_de[finca_id]] += Decimal(area)
    usuarios: dict[str, set[uuid.UUID]] = defaultdict(set)
    for finca_id, usuario_id in await _filas(
        db, select(FincaUsuario.finca_id, FincaUsuario.usuario_id)
    ):
        usuarios[zona_de[finca_id]].add(usuario_id)

    siembras: dict[str, int] = defaultdict(int)
    area_sembrada: dict[str, Decimal] = defaultdict(Decimal)
    por_cultivo: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    nombres = {c.id: c.nombre for c in await db.scalars(select(Cultivo))}
    for finca_id, cultivo_id, area in await _filas(
        db, select(Siembra.finca_id, Siembra.cultivo_id, Siembra.area_ha)
    ):
        zona = zona_de[finca_id]
        siembras[zona] += 1
        area_sembrada[zona] += Decimal(area)
        por_cultivo[zona][nombres[cultivo_id]] += 1

    cosechas: dict[str, int] = defaultdict(int)
    produccion: dict[str, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    for finca_id, kilos, unidad in await _filas(
        db,
        select(Cosecha.finca_id, Cosecha.cantidad, Cosecha.unidad).where(
            Cosecha.estado == "activa"
        ),
    ):
        zona = zona_de[finca_id]
        cosechas[zona] += 1
        produccion[zona][unidad] += Decimal(kilos)

    gastos = sumar(
        await _filas(db, select(Gasto.finca_id, Gasto.monto).where(Gasto.estado == "activo"))
    )
    ingresos = sumar(
        await _filas(db, select(Ingreso.finca_id, Ingreso.total).where(Ingreso.estado == "activo"))
    )
    salida = []
    for zona in sorted(fincas):
        ranking = sorted(por_cultivo[zona].items(), key=lambda par: (-par[1], par[0]))
        salida.append(
            EstadisticaZona(
                zona=zona,
                fincas=fincas[zona],
                agricultores=len(usuarios[zona]),
                area_ha_fincas=area_fincas[zona],
                siembras=siembras[zona],
                area_sembrada_ha=area_sembrada[zona],
                cosechas=cosechas[zona],
                produccion=_por_unidad(produccion[zona]),
                gastos=gastos[zona],
                ingresos=ingresos[zona],
                utilidad=ingresos[zona] - gastos[zona],
                gasto_por_ha=gastos[zona] / area_sembrada[zona] if area_sembrada[zona] else None,
                cultivos_principales=[nombre for nombre, _ in ranking[:3]],
            )
        )
    return salida
