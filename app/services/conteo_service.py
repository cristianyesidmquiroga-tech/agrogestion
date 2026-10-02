"""Conteo de plantas, índices por planta, cronograma y necesidad de insumos."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.catalogos import fases_del_ciclo
from app.core.exceptions import ReglaNegocio
from app.models.entities import Usuario
from app.models.siembra import ConteoPlanta
from app.schemas.siembra import (
    ConteoCrear,
    CronogramaSalida,
    FaseCronograma,
    IndicesSalida,
    NecesidadItem,
    NecesidadSalida,
)
from app.services import explicacion_service, siembra_service
from app.utils.fechas import a_dia


async def _ultimo(
    db: AsyncSession, siembra_id: uuid.UUID, corte: date | None = None
) -> ConteoPlanta | None:
    consulta = select(ConteoPlanta).where(ConteoPlanta.siembra_id == siembra_id)
    if corte:
        consulta = consulta.where(ConteoPlanta.fecha <= corte)
    fila: ConteoPlanta | None = await db.scalar(
        consulta.order_by(ConteoPlanta.fecha.desc(), ConteoPlanta.creado_en.desc()).limit(1)
    )
    return fila


async def listar(db: AsyncSession, usuario: Usuario, siembra_id: uuid.UUID) -> list[ConteoPlanta]:
    await siembra_service.obtener(db, usuario, siembra_id)
    filas = await db.scalars(
        select(ConteoPlanta)
        .where(ConteoPlanta.siembra_id == siembra_id)
        .order_by(ConteoPlanta.fecha.desc())
    )
    return list(filas)


async def crear(
    db: AsyncSession, usuario: Usuario, siembra_id: uuid.UUID, datos: ConteoCrear
) -> ConteoPlanta:
    siembra = await siembra_service.obtener(db, usuario, siembra_id)
    if siembra.cultivo.unidad_conteo != "planta":
        raise ReglaNegocio("Este cultivo se trabaja por área, no por planta.", "CONTEO_NO_APLICA")
    if siembra.estado not in siembra_service.ESTADOS_ACTIVOS:
        raise ReglaNegocio("La siembra ya no admite conteos.", "SIEMBRA_ESTADO_INVALIDO")
    previas = await db.scalar(
        select(func.coalesce(func.sum(ConteoPlanta.resiembras), 0)).where(
            ConteoPlanta.siembra_id == siembra_id
        )
    )
    tope = (siembra.plantas_sembradas or 0) + int(previas or 0) + datos.resiembras
    if datos.vivas > tope:
        raise ReglaNegocio(
            f"Las plantas vivas no pueden superar las {tope} sembradas y resembradas.",
            "CONTEO_INVALIDO",
        )
    conteo = ConteoPlanta(
        siembra_id=siembra_id,
        fecha=datos.fecha,
        vivas=datos.vivas,
        muertas=datos.muertas,
        resiembras=datos.resiembras,
        creado_por=usuario.id,
    )
    db.add(conteo)
    await db.commit()
    return conteo


async def indices(db: AsyncSession, usuario: Usuario, siembra_id: uuid.UUID) -> IndicesSalida:
    siembra = await siembra_service.obtener(db, usuario, siembra_id)
    if siembra.cultivo.unidad_conteo != "planta":
        return IndicesSalida(
            siembra_id=siembra_id,
            fecha_conteo=None,
            indicadores=[],
            aviso="Este cultivo se trabaja por área; los índices por planta no aplican.",
        )
    conteo = await _ultimo(db, siembra_id)
    if conteo is None:
        return IndicesSalida(
            siembra_id=siembra_id,
            fecha_conteo=None,
            indicadores=[],
            aviso="Cuente sus plantas para ver los índices por planta.",
        )
    total_resiembras = await db.scalar(
        select(func.coalesce(func.sum(ConteoPlanta.resiembras), 0)).where(
            ConteoPlanta.siembra_id == siembra_id
        )
    )
    plantadas = (siembra.plantas_sembradas or 0) + int(total_resiembras or 0)
    return IndicesSalida(
        siembra_id=siembra_id,
        fecha_conteo=conteo.fecha,
        indicadores=explicacion_service.indicadores_de_poblacion(
            vivas=conteo.vivas,
            plantadas=plantadas,
            area_ha=siembra.area_ha,
            densidad_ref=siembra.cultivo.densidad_ref,
            ref_por_validar=siembra.cultivo.por_validar,
            fecha=conteo.fecha,
        ),
    )


async def cronograma(db: AsyncSession, usuario: Usuario, ciclo_id: uuid.UUID) -> CronogramaSalida:
    ciclo, siembra = await siembra_service.obtener_ciclo(db, usuario, ciclo_id)
    validas = fases_del_ciclo(siembra.cultivo.tipo_ciclo, ciclo.tipo or "levante")
    fases = [f for f in siembra.cultivo.fases if f.fase in validas]
    cursor = a_dia(ciclo.fecha_inicio)
    salida: list[FaseCronograma] = []
    for f in fases:
        inicio = cursor
        fin = (
            inicio + timedelta(days=f.dias_estimados)
            if inicio and f.dias_estimados is not None
            else None
        )
        salida.append(
            FaseCronograma(
                fase=f.fase,
                orden=f.orden,
                dias_estimados=f.dias_estimados,
                por_validar=f.por_validar,
                inicio_plan=inicio,
                fin_plan=fin,
            )
        )
        cursor = fin
    aviso = None
    if not fases:
        aviso = "El perfil de este cultivo aún no tiene fases cargadas."
    elif ciclo.fecha_inicio is None:
        aviso = "Las fechas se calculan cuando el ciclo inicia."
    return CronogramaSalida(
        ciclo_id=ciclo_id,
        tipo=ciclo.tipo or "levante",
        fecha_inicio=a_dia(ciclo.fecha_inicio),
        fases=salida,
        aviso=aviso,
    )


async def necesidad_insumos(
    db: AsyncSession, usuario: Usuario, ciclo_id: uuid.UUID
) -> NecesidadSalida:
    _, siembra = await siembra_service.obtener_ciclo(db, usuario, ciclo_id)
    cultivo = siembra.cultivo
    if not cultivo.dosis:
        return NecesidadSalida(
            ciclo_id=ciclo_id,
            items=[],
            aviso="Falta cargar las dosis de este cultivo desde una fuente técnica.",
        )
    conteo = await _ultimo(db, siembra.id) if cultivo.unidad_conteo == "planta" else None
    items: list[NecesidadItem] = []
    for d in cultivo.dosis:
        cantidad: Decimal | None = None
        mensaje: str | None = None
        if d.base == "hectarea":
            cantidad = siembra.area_ha * d.dosis
        elif conteo is not None:
            cantidad = Decimal(conteo.vivas) * d.dosis
        else:
            mensaje = "Cuente las plantas para calcular esta cantidad."
        items.append(
            NecesidadItem(
                insumo_tipo=d.insumo_tipo,
                dosis=d.dosis,
                unidad=d.unidad,
                base=d.base,
                cantidad_necesaria=float(cantidad) if cantidad is not None else None,
                por_validar=d.por_validar,
                mensaje=mensaje,
            )
        )
    return NecesidadSalida(ciclo_id=ciclo_id, items=items)
