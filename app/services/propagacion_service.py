import uuid

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NoEncontrado, ReglaNegocio
from app.models.entities import Usuario
from app.models.siembra import LotePropagacion
from app.schemas.propagacion import PropagacionActualizar, PropagacionCrear, TrasplanteEntrada
from app.services import cultivo_service, siembra_service
from app.services.acceso_service import exigir_finca, ids_fincas


async def listar(
    db: AsyncSession, usuario: Usuario, pendientes: bool | None, skip: int, limit: int
) -> tuple[list[LotePropagacion], int]:
    filtros: list[ColumnElement[bool]] = [
        LotePropagacion.finca_id.in_(await ids_fincas(db, usuario))
    ]
    if pendientes is True:
        filtros.append(
            LotePropagacion.trasplantadas < LotePropagacion.puestas - LotePropagacion.perdidas
        )
    total = await db.scalar(select(func.count()).select_from(LotePropagacion).where(*filtros)) or 0
    filas = await db.scalars(
        select(LotePropagacion)
        .where(*filtros)
        .order_by(LotePropagacion.fecha_inicio.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(filas), total


async def obtener(db: AsyncSession, usuario: Usuario, lote_id: uuid.UUID) -> LotePropagacion:
    lote = await db.get(LotePropagacion, lote_id)
    if lote is None:
        raise NoEncontrado("No encontramos ese lote de vivero.", "PROPAGACION_NO_ENCONTRADA")
    await exigir_finca(
        db,
        usuario,
        lote.finca_id,
        "No encontramos ese lote de vivero.",
        "PROPAGACION_NO_ENCONTRADA",
    )
    return lote


async def crear(db: AsyncSession, usuario: Usuario, datos: PropagacionCrear) -> LotePropagacion:
    await exigir_finca(db, usuario, datos.finca_id)
    cultivo = await cultivo_service.obtener(db, datos.cultivo_id)
    metodos = {m.metodo for m in cultivo.metodos}
    if metodos and datos.metodo not in metodos:
        raise ReglaNegocio("Este cultivo no se propaga con ese método.", "METODO_NO_VALIDO")
    lote = LotePropagacion(
        finca_id=datos.finca_id,
        cultivo_id=datos.cultivo_id,
        metodo=datos.metodo,
        fecha_inicio=datos.fecha_inicio,
        puestas=datos.puestas,
        creado_por=usuario.id,
    )
    db.add(lote)
    await db.commit()
    return lote


async def actualizar(
    db: AsyncSession, usuario: Usuario, lote_id: uuid.UUID, datos: PropagacionActualizar
) -> LotePropagacion:
    lote = await obtener(db, usuario, lote_id)
    germinadas = lote.germinadas if datos.germinadas is None else datos.germinadas
    listas = lote.listas if datos.listas is None else datos.listas
    perdidas = lote.perdidas if datos.perdidas is None else datos.perdidas
    if germinadas > lote.puestas:
        raise ReglaNegocio("Las germinadas no pueden superar las puestas.", "PROPAGACION_INVALIDA")
    if listas > germinadas:
        raise ReglaNegocio(
            "Las plantas listas no pueden superar las germinadas.", "PROPAGACION_INVALIDA"
        )
    if perdidas > lote.puestas:
        raise ReglaNegocio("Las pérdidas no pueden superar las puestas.", "PROPAGACION_INVALIDA")
    if listas < lote.trasplantadas:
        raise ReglaNegocio(
            "Ya se trasplantaron más plantas que esas listas.", "PROPAGACION_INVALIDA"
        )
    lote.germinadas, lote.listas, lote.perdidas = germinadas, listas, perdidas
    await db.commit()
    return lote


async def trasplantar(
    db: AsyncSession, usuario: Usuario, lote_id: uuid.UUID, datos: TrasplanteEntrada
) -> LotePropagacion:
    lote = await obtener(db, usuario, lote_id)
    siembra = await siembra_service.obtener(db, usuario, datos.siembra_id)
    if siembra.finca_id != lote.finca_id or siembra.cultivo_id != lote.cultivo_id:
        raise ReglaNegocio(
            "La siembra debe ser de la misma finca y el mismo cultivo.", "TRASPLANTE_INVALIDO"
        )
    disponibles = lote.listas - lote.trasplantadas
    if datos.cantidad > disponibles:
        raise ReglaNegocio(
            f"Solo hay {disponibles} plantas listas para trasplantar.", "TRASPLANTE_INVALIDO"
        )
    lote.trasplantadas += datos.cantidad
    lote.siembra_id = siembra.id
    siembra.plantas_sembradas = (siembra.plantas_sembradas or 0) + datos.cantidad
    await db.commit()
    return lote
