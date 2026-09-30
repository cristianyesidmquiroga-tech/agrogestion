"""Reportes con los datos que ya existen. Los de dinero y mano de obra llegan con sus módulos."""

import uuid
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.contexto import UsuarioActual
from app.models.riesgo import EventoAdverso, Riesgo
from app.models.siembra import Siembra
from app.schemas.inicio import (
    CicloCronograma,
    EventosPorTipo,
    IndiceSiembra,
    ReporteCronograma,
    ReporteDisponible,
    ReporteEventos,
    ReporteIndices,
)
from app.services import calendario, conteo_service
from app.services.acceso_service import exigir_finca, ids_fincas

PRODUCCION = ["admin", "agricultor"]
CON_CONTADOR = ["admin", "agricultor", "contador"]
PENDIENTE_DINERO = "Depende del módulo de dinero, que aún no está listo."

CATALOGO = [
    (
        "indices",
        "Índices por planta",
        "Plantas por hectárea y plantas perdidas de cada siembra.",
        True,
        None,
        CON_CONTADOR,
    ),
    (
        "cronograma",
        "Tiempos del ciclo",
        "En qué fase va cada ciclo y cuándo debería terminar.",
        True,
        None,
        CON_CONTADOR,
    ),
    (
        "eventos",
        "Eventos adversos",
        "Cuántos eventos hubo y cuánto costaron.",
        True,
        None,
        PRODUCCION,
    ),
    (
        "costos",
        "Costos por ciclo",
        "Cuánto cuesta cada ciclo, por hectárea y por planta.",
        False,
        PENDIENTE_DINERO,
        CON_CONTADOR,
    ),
    (
        "utilidad",
        "Utilidad",
        "Ingresos menos costos de cada ciclo.",
        False,
        PENDIENTE_DINERO,
        ["admin", "contador"],
    ),
    (
        "flujo-caja",
        "Flujo de caja",
        "Ingresos, gastos y saldo por mes.",
        False,
        PENDIENTE_DINERO,
        CON_CONTADOR,
    ),
    (
        "mano-obra",
        "Mano de obra",
        "Jornales y costo de cada labor.",
        False,
        "Depende del módulo de labores y jornales.",
        CON_CONTADOR,
    ),
    (
        "procesos",
        "Procesos",
        "Rendimiento, merma y costo por lote de proceso.",
        False,
        "Depende del módulo de procesos.",
        PRODUCCION,
    ),
]


def catalogo(usuario: UsuarioActual) -> list[ReporteDisponible]:
    return [
        ReporteDisponible(id=i, titulo=t, descripcion=d, disponible=ok, motivo=motivo, roles=roles)
        for i, t, d, ok, motivo, roles in CATALOGO
        if usuario.rol in roles
    ]


async def _siembras_activas(
    db: AsyncSession, usuario: UsuarioActual, finca_id: uuid.UUID | None
) -> list[Siembra]:
    if finca_id:
        await exigir_finca(db, usuario, finca_id)
        fincas = [finca_id]
    else:
        fincas = await ids_fincas(db, usuario)
    filas = await db.scalars(
        select(Siembra)
        .where(Siembra.finca_id.in_(fincas), Siembra.estado.in_(("planeada", "en_curso")))
        .order_by(Siembra.creado_en.desc())
    )
    return list(filas)


async def indices(
    db: AsyncSession, usuario: UsuarioActual, finca_id: uuid.UUID | None
) -> ReporteIndices:
    salida = []
    for siembra in await _siembras_activas(db, usuario, finca_id):
        detalle = await conteo_service.indices(db, usuario, siembra.id)
        salida.append(
            IndiceSiembra(
                siembra_id=siembra.id,
                cultivo=siembra.cultivo.nombre,
                lote_id=siembra.lote_id,
                fecha_conteo=detalle.fecha_conteo,
                indicadores=detalle.indicadores,
                aviso=detalle.aviso,
            )
        )
    return ReporteIndices(siembras=salida)


async def cronograma(
    db: AsyncSession, usuario: UsuarioActual, finca_id: uuid.UUID | None, hoy: date | None = None
) -> ReporteCronograma:
    hoy = hoy or date.today()
    salida = []
    for siembra in await _siembras_activas(db, usuario, finca_id):
        for ciclo in (c for c in siembra.ciclos if c.estado != "cerrado"):
            avance = calendario.avance_del_ciclo(siembra, ciclo, hoy)
            salida.append(
                CicloCronograma(
                    siembra_id=siembra.id,
                    ciclo_id=ciclo.id,
                    cultivo=siembra.cultivo.nombre,
                    tipo=ciclo.tipo,
                    fecha_inicio=ciclo.fecha_inicio,
                    fase_actual=avance.fase_actual,
                    fases_planeadas=avance.fases_planeadas,
                    fecha_fin_planeada=avance.fecha_fin_planeada,
                    aviso=avance.aviso,
                )
            )
    return ReporteCronograma(ciclos=salida)


async def eventos(
    db: AsyncSession,
    usuario: UsuarioActual,
    finca_id: uuid.UUID | None,
    desde: date | None,
    hasta: date | None,
) -> ReporteEventos:
    if finca_id:
        await exigir_finca(db, usuario, finca_id)
        fincas = [finca_id]
    else:
        fincas = await ids_fincas(db, usuario)
    filtros: list[ColumnElement[bool]] = [EventoAdverso.finca_id.in_(fincas)]
    if desde:
        filtros.append(EventoAdverso.inicio >= desde)
    if hasta:
        filtros.append(EventoAdverso.inicio <= hasta)
    filas = (
        await db.execute(
            select(EventoAdverso, Riesgo.tipo)
            .join(Riesgo, Riesgo.id == EventoAdverso.riesgo_id)
            .where(*filtros)
        )
    ).all()
    por_tipo: dict[str, list[EventoAdverso]] = defaultdict(list)
    for evento, tipo in filas:
        por_tipo[tipo].append(evento)
    resumen = []
    for tipo in sorted(por_tipo):
        lista = por_tipo[tipo]
        porcentajes = [float(e.perdida_pct) for e in lista if e.perdida_pct is not None]
        resumen.append(
            EventosPorTipo(
                tipo=tipo,
                cantidad=len(lista),
                perdida_estimada=sum((e.perdida_estimada or Decimal(0) for e in lista), Decimal(0)),
                perdida_promedio_pct=round(sum(porcentajes) / len(porcentajes), 1)
                if porcentajes
                else None,
            )
        )
    return ReporteEventos(
        desde=desde,
        hasta=hasta,
        total=len(filas),
        perdida_estimada_total=sum((r.perdida_estimada for r in resumen), Decimal(0)),
        por_tipo=resumen,
        por_severidad=dict(Counter(e.severidad for e, _ in filas)),
        aviso=None if filas else "No hay eventos registrados en este periodo.",
    )
