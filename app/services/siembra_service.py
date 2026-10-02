import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from app.models.entities import Ciclo, Cosecha, Lote, Usuario
from app.models.siembra import Siembra
from app.schemas.siembra import CerrarCicloEntrada, SiembraCrear
from app.services import cultivo_service
from app.services.acceso_service import exigir_finca, ids_fincas
from app.utils.fechas import a_fecha_hora

ESTADOS_ACTIVOS = ("planeada", "en_curso")


async def listar(
    db: AsyncSession,
    usuario: Usuario,
    estado: str | None,
    finca_id: uuid.UUID | None,
    skip: int,
    limit: int,
) -> tuple[list[Siembra], int]:
    fincas = await ids_fincas(db, usuario)
    filtros: list[ColumnElement[bool]] = [Siembra.finca_id.in_(fincas)]
    if estado:
        filtros.append(Siembra.estado == estado)
    if finca_id:
        filtros.append(Siembra.finca_id == finca_id)
    total = await db.scalar(select(func.count()).select_from(Siembra).where(*filtros)) or 0
    filas = await db.scalars(
        select(Siembra).where(*filtros).order_by(Siembra.creado_en.desc()).offset(skip).limit(limit)
    )
    return list(filas), total


async def obtener(db: AsyncSession, usuario: Usuario, siembra_id: uuid.UUID) -> Siembra:
    siembra = await db.get(Siembra, siembra_id)
    if siembra is None:
        raise NoEncontrado("No encontramos esa siembra.", "SIEMBRA_NO_ENCONTRADA")
    await exigir_finca(
        db, usuario, siembra.finca_id, "No encontramos esa siembra.", "SIEMBRA_NO_ENCONTRADA"
    )
    return siembra


async def area_ocupada(db: AsyncSession, lote_id: uuid.UUID) -> Decimal:
    suma = await db.scalar(
        select(func.coalesce(func.sum(Siembra.area_ha), 0)).where(
            Siembra.lote_id == lote_id, Siembra.estado.in_(ESTADOS_ACTIVOS)
        )
    )
    return Decimal(str(suma or 0))


async def crear(db: AsyncSession, usuario: Usuario, datos: SiembraCrear) -> Siembra:
    await exigir_finca(db, usuario, datos.finca_id)
    lote = await db.scalar(
        select(Lote)
        .where(Lote.id == datos.lote_id, Lote.finca_id == datos.finca_id)
        .with_for_update()
    )
    if lote is None:
        raise NoEncontrado("No encontramos ese lote en la finca.", "LOTE_NO_ENCONTRADO")
    cultivo = await cultivo_service.obtener(db, datos.cultivo_id)
    metodos = {m.metodo for m in cultivo.metodos}
    if metodos and datos.metodo not in metodos:
        raise ReglaNegocio("Este cultivo no se propaga con ese método.", "METODO_NO_VALIDO")
    if cultivo.unidad_conteo == "planta" and datos.plantas_sembradas is None:
        raise ReglaNegocio("Indique cuántas plantas va a sembrar.", "PLANTAS_OBLIGATORIAS")
    libre = lote.area - await area_ocupada(db, lote.id)
    if datos.area_ha > libre:
        raise ReglaNegocio(f"El lote solo tiene {libre:.4f} hectáreas libres.", "AREA_SUPERA_LOTE")
    siembra = Siembra(
        finca_id=datos.finca_id,
        lote_id=datos.lote_id,
        cultivo_id=datos.cultivo_id,
        metodo=datos.metodo,
        area_ha=datos.area_ha,
        plantas_sembradas=datos.plantas_sembradas,
        fecha_plan=datos.fecha_plan,
        presupuesto=datos.presupuesto,
        estado="planeada",
        creado_por=usuario.id,
    )
    db.add(siembra)
    await db.flush()
    db.add(
        Ciclo(
            finca_id=siembra.finca_id,
            siembra_id=siembra.id,
            nombre="levante 1",
            tipo="levante",
            numero=1,
            estado="planeado",
            creado_por=usuario.id,
        )
    )
    await db.commit()
    await db.refresh(siembra, attribute_names=["ciclos"])
    return siembra


async def iniciar(
    db: AsyncSession, usuario: Usuario, siembra_id: uuid.UUID, fecha: date | None
) -> Siembra:
    siembra = await obtener(db, usuario, siembra_id)
    if siembra.estado != "planeada":
        raise ReglaNegocio("Solo se puede iniciar una siembra planeada.", "SIEMBRA_ESTADO_INVALIDO")
    siembra.estado = "en_curso"
    primero = next((c for c in siembra.ciclos if c.estado == "planeado"), None)
    if primero:
        primero.estado = "abierto"
        primero.fecha_inicio = a_fecha_hora(fecha or date.today())
    await db.commit()
    return siembra


async def cancelar(db: AsyncSession, usuario: Usuario, siembra_id: uuid.UUID) -> Siembra:
    siembra = await obtener(db, usuario, siembra_id)
    if siembra.estado not in ESTADOS_ACTIVOS:
        raise ReglaNegocio("Esta siembra ya está cerrada o cancelada.", "SIEMBRA_ESTADO_INVALIDO")
    siembra.estado = "cancelada"
    for ciclo in siembra.ciclos:
        if ciclo.estado != "cerrado":
            ciclo.estado = "cerrado"
            ciclo.fecha_fin = a_fecha_hora(date.today())
            ciclo.motivo_perdida = "Siembra cancelada"
    await db.commit()
    return siembra


async def _ciclo(db: AsyncSession, usuario: Usuario, ciclo_id: uuid.UUID) -> tuple[Ciclo, Siembra]:
    ciclo = await db.get(Ciclo, ciclo_id)
    if ciclo is None or ciclo.siembra_id is None:
        raise NoEncontrado("No encontramos ese ciclo.", "CICLO_NO_ENCONTRADO")
    return ciclo, await obtener(db, usuario, ciclo.siembra_id)


async def obtener_ciclo(
    db: AsyncSession, usuario: Usuario, ciclo_id: uuid.UUID
) -> tuple[Ciclo, Siembra]:
    return await _ciclo(db, usuario, ciclo_id)


async def crear_ciclo(
    db: AsyncSession, usuario: Usuario, siembra_id: uuid.UUID, tipo: str
) -> Ciclo:
    siembra = await obtener(db, usuario, siembra_id)
    cultivo = siembra.cultivo
    if siembra.estado != "en_curso":
        raise ReglaNegocio(
            "La siembra debe estar en curso para abrir un ciclo.", "SIEMBRA_ESTADO_INVALIDO"
        )
    if cultivo.tipo_ciclo == "transitorio":
        raise ReglaNegocio("Este cultivo tiene un solo ciclo.", "CICLO_TIPO_NO_VALIDO")
    if any(c.estado != "cerrado" for c in siembra.ciclos):
        raise Conflicto("Cierre el ciclo actual antes de abrir otro.", "CICLO_ACTIVO")
    ultimo = siembra.ciclos[-1] if siembra.ciclos else None
    if tipo == "renovacion" and cultivo.tipo_renovacion is None:
        raise ReglaNegocio("Este cultivo no tiene renovación.", "CICLO_TIPO_NO_VALIDO")
    if tipo == "levante" and (ultimo is None or ultimo.tipo != "renovacion"):
        raise ReglaNegocio("Un nuevo levante solo sigue a una renovación.", "CICLO_TIPO_NO_VALIDO")
    numero = (ultimo.numero + 1) if ultimo and ultimo.numero else 1
    ciclo = Ciclo(
        finca_id=siembra.finca_id,
        siembra_id=siembra.id,
        nombre=f"{tipo} {numero}",
        tipo=tipo,
        numero=numero,
        estado="planeado",
        creado_por=usuario.id,
    )
    db.add(ciclo)
    await db.commit()
    return ciclo


async def iniciar_ciclo(
    db: AsyncSession, usuario: Usuario, ciclo_id: uuid.UUID, fecha: date | None
) -> Ciclo:
    ciclo, siembra = await _ciclo(db, usuario, ciclo_id)
    if siembra.estado != "en_curso":
        raise ReglaNegocio("La siembra debe estar en curso.", "SIEMBRA_ESTADO_INVALIDO")
    if ciclo.estado != "planeado":
        raise ReglaNegocio("Solo se puede iniciar un ciclo planeado.", "CICLO_ESTADO_INVALIDO")
    if any(c.estado == "abierto" for c in siembra.ciclos):
        raise Conflicto("Ya hay un ciclo en curso en esta siembra.", "CICLO_ACTIVO")
    ciclo.estado = "abierto"
    ciclo.fecha_inicio = a_fecha_hora(fecha or date.today())
    await db.commit()
    return ciclo


async def cerrar_ciclo(
    db: AsyncSession, usuario: Usuario, ciclo_id: uuid.UUID, datos: CerrarCicloEntrada
) -> Ciclo:
    ciclo, siembra = await _ciclo(db, usuario, ciclo_id)
    if ciclo.estado != "abierto":
        raise ReglaNegocio("Solo se puede cerrar un ciclo en curso.", "CICLO_ESTADO_INVALIDO")
    hay_cosecha = await db.scalar(
        select(func.count())
        .select_from(Cosecha)
        .where(Cosecha.ciclo_id == ciclo.id, Cosecha.estado == "activa")
    )
    if not hay_cosecha and not datos.motivo_perdida:
        raise ReglaNegocio(
            "Registre una cosecha o explique el motivo de la pérdida para cerrar el ciclo.",
            "CICLO_SIN_COSECHA",
        )
    ciclo.estado = "cerrado"
    ciclo.fecha_fin = a_fecha_hora(datos.fecha_fin or date.today())
    ciclo.motivo_perdida = datos.motivo_perdida
    if siembra.cultivo.tipo_ciclo == "transitorio":
        siembra.estado = "cerrada"
    await db.commit()
    return ciclo
