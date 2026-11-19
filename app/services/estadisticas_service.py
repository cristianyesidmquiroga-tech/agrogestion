from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Ciclo,
    Cosecha,
    EventoAdverso,
    Finca,
    Gasto,
    Ingreso,
    Siembra,
    Trabajador,
    Usuario,
)
from app.schemas.estadisticas import (
    CostosGenerales,
    PuntoMensual,
    ResumenGeneral,
    TotalPorCategoria,
)

CERO = Decimal(0)


async def _numero(db: AsyncSession, consulta: Select[Any]) -> int:
    return int(await db.scalar(consulta) or 0)


async def _suma(db: AsyncSession, consulta: Select[Any]) -> Decimal:
    return Decimal(await db.scalar(consulta) or 0)


async def _agrupado(db: AsyncSession, columna: Any, *filtros: Any) -> dict[str, int]:
    consulta = select(columna, func.count()).where(*filtros).group_by(columna)
    return {str(clave): int(n) for clave, n in (await db.execute(consulta)).all()}


def _gastos_activos() -> Select[Any]:
    return select(func.coalesce(func.sum(Gasto.monto), 0)).where(Gasto.estado == "activo")


def _ingresos_activos() -> Select[Any]:
    return select(func.coalesce(func.sum(Ingreso.total), 0)).where(Ingreso.estado == "activo")


async def resumen(db: AsyncSession) -> ResumenGeneral:
    usuarios_por_rol = await _agrupado(db, Usuario.rol)
    siembras_por_estado = await _agrupado(db, Siembra.estado)
    gastos = await _suma(db, _gastos_activos())
    ingresos = await _suma(db, _ingresos_activos())
    return ResumenGeneral(
        usuarios=sum(usuarios_por_rol.values()),
        usuarios_activos=await _numero(
            db, select(func.count()).select_from(Usuario).where(Usuario.activo.is_(True))
        ),
        usuarios_por_rol=usuarios_por_rol,
        fincas=await _numero(db, select(func.count()).select_from(Finca)),
        area_ha_fincas=await _suma(db, select(func.coalesce(func.sum(Finca.area_ha), 0))),
        siembras=sum(siembras_por_estado.values()),
        siembras_por_estado=siembras_por_estado,
        ciclos_abiertos=await _numero(
            db, select(func.count()).select_from(Ciclo).where(Ciclo.estado == "abierto")
        ),
        ciclos_cerrados=await _numero(
            db, select(func.count()).select_from(Ciclo).where(Ciclo.estado == "cerrado")
        ),
        cosechas=await _numero(
            db, select(func.count()).select_from(Cosecha).where(Cosecha.estado == "activa")
        ),
        trabajadores=await _numero(
            db, select(func.count()).select_from(Trabajador).where(Trabajador.estado == "activo")
        ),
        gastos=gastos,
        ingresos=ingresos,
        utilidad=ingresos - gastos,
        eventos_adversos=await _numero(db, select(func.count()).select_from(EventoAdverso)),
        perdida_estimada=await _suma(
            db, select(func.coalesce(func.sum(EventoAdverso.perdida_estimada), 0))
        ),
    )


def _meses(cantidad: int, hoy: datetime) -> list[tuple[int, int]]:
    anio, mes = hoy.year, hoy.month
    lista = []
    for _ in range(cantidad):
        lista.append((anio, mes))
        anio, mes = (anio - 1, 12) if mes == 1 else (anio, mes - 1)
    return lista[::-1]


async def _por_mes(
    db: AsyncSession, fecha: Any, valor: Any, desde: datetime, *filtros: Any
) -> dict[tuple[int, int], Decimal]:
    anio, mes = extract("year", fecha), extract("month", fecha)
    consulta = select(anio, mes, valor).where(fecha >= desde, *filtros).group_by(anio, mes)
    return {(int(a), int(m)): Decimal(v or 0) for a, m, v in (await db.execute(consulta)).all()}


async def crecimiento(db: AsyncSession, meses: int) -> list[PuntoMensual]:
    hoy = datetime.now(UTC)
    ventana = _meses(meses, hoy)
    desde = datetime(ventana[0][0], ventana[0][1], 1, tzinfo=UTC)
    conteo = func.count()
    series = {
        "usuarios": await _por_mes(db, Usuario.creado_en, conteo, desde),
        "fincas": await _por_mes(db, Finca.creado_en, conteo, desde),
        "siembras": await _por_mes(db, Siembra.creado_en, conteo, desde),
        "cosechas": await _por_mes(db, Cosecha.fecha, conteo, desde, Cosecha.estado == "activa"),
        "gastos": await _por_mes(
            db, Gasto.fecha, func.sum(Gasto.monto), desde, Gasto.estado == "activo"
        ),
        "ingresos": await _por_mes(
            db, Ingreso.fecha, func.sum(Ingreso.total), desde, Ingreso.estado == "activo"
        ),
    }
    return [
        PuntoMensual(
            mes=f"{a}-{m:02d}",
            usuarios=int(series["usuarios"].get((a, m), 0)),
            fincas=int(series["fincas"].get((a, m), 0)),
            siembras=int(series["siembras"].get((a, m), 0)),
            cosechas=int(series["cosechas"].get((a, m), 0)),
            gastos=series["gastos"].get((a, m), CERO),
            ingresos=series["ingresos"].get((a, m), CERO),
        )
        for a, m in ventana
    ]


async def _por_categoria(db: AsyncSession, modelo: Any, valor: Any) -> list[TotalPorCategoria]:
    total = func.coalesce(func.sum(valor), 0)
    consulta = (
        select(modelo.categoria, func.count(), total)
        .where(modelo.estado == "activo")
        .group_by(modelo.categoria)
        .order_by(total.desc(), modelo.categoria)
    )
    return [
        TotalPorCategoria(categoria=c, registros=int(n), total=Decimal(t))
        for c, n, t in (await db.execute(consulta)).all()
    ]


async def costos(db: AsyncSession) -> CostosGenerales:
    gastos = await _suma(db, _gastos_activos())
    ingresos = await _suma(db, _ingresos_activos())
    area = await _suma(
        db,
        select(func.coalesce(func.sum(Siembra.area_ha), 0)).where(
            Siembra.estado.in_(("en_curso", "cerrada"))
        ),
    )
    return CostosGenerales(
        gastos_por_categoria=await _por_categoria(db, Gasto, Gasto.monto),
        ingresos_por_categoria=await _por_categoria(db, Ingreso, Ingreso.total),
        gastos=gastos,
        ingresos=ingresos,
        area_sembrada_ha=area,
        gasto_por_ha=gastos / area if area else None,
        ingreso_por_ha=ingresos / area if area else None,
    )
