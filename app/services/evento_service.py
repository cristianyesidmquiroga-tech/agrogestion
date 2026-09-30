import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.contexto import UsuarioActual
from app.core.exceptions import NoEncontrado, ReglaNegocio
from app.models.riesgo import EventoAdverso, Riesgo
from app.models.siembra import Ciclo, Siembra
from app.schemas.evento import EventoActualizar, EventoCrear
from app.services.acceso_service import exigir_finca, ids_fincas


async def listar(
    db: AsyncSession,
    usuario: UsuarioActual,
    tipo: str | None,
    finca_id: uuid.UUID | None,
    skip: int,
    limit: int,
) -> tuple[list[EventoAdverso], int]:
    base = select(EventoAdverso).where(EventoAdverso.finca_id.in_(await ids_fincas(db, usuario)))
    if tipo:
        base = base.join(Riesgo, Riesgo.id == EventoAdverso.riesgo_id).where(Riesgo.tipo == tipo)
    if finca_id:
        base = base.where(EventoAdverso.finca_id == finca_id)
    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0
    filas = await db.scalars(base.order_by(EventoAdverso.inicio.desc()).offset(skip).limit(limit))
    return list(filas), total


async def obtener(db: AsyncSession, usuario: UsuarioActual, evento_id: uuid.UUID) -> EventoAdverso:
    evento = await db.get(EventoAdverso, evento_id)
    if evento is None:
        raise NoEncontrado("No encontramos ese evento.", "EVENTO_NO_ENCONTRADO")
    await exigir_finca(
        db, usuario, evento.finca_id, "No encontramos ese evento.", "EVENTO_NO_ENCONTRADO"
    )
    return evento


async def crear(db: AsyncSession, usuario: UsuarioActual, datos: EventoCrear) -> EventoAdverso:
    await exigir_finca(db, usuario, datos.finca_id)
    if await db.get(Riesgo, datos.riesgo_id) is None:
        raise NoEncontrado("No encontramos ese riesgo.", "RIESGO_NO_ENCONTRADO")
    if datos.siembra_id:
        siembra = await db.get(Siembra, datos.siembra_id)
        if siembra is None or siembra.finca_id != datos.finca_id:
            raise ReglaNegocio("Esa siembra no pertenece a la finca.", "SIEMBRA_NO_VALIDA")
    if datos.ciclo_id:
        ciclo = await db.get(Ciclo, datos.ciclo_id)
        dueno = await db.get(Siembra, ciclo.siembra_id) if ciclo else None
        if dueno is None or dueno.finca_id != datos.finca_id:
            raise ReglaNegocio("Ese ciclo no pertenece a la finca.", "CICLO_NO_VALIDO")
    evento = EventoAdverso(**datos.model_dump(), creado_por=usuario.id)
    db.add(evento)
    await db.commit()
    return evento


async def actualizar(
    db: AsyncSession, usuario: UsuarioActual, evento_id: uuid.UUID, datos: EventoActualizar
) -> EventoAdverso:
    evento = await obtener(db, usuario, evento_id)
    cambios = datos.model_dump(exclude_unset=True)
    fin = cambios.get("fin", evento.fin)
    if fin is not None and fin < evento.inicio:
        raise ReglaNegocio(
            "La fecha final no puede ser anterior a la inicial.", "EVENTO_FECHAS_INVALIDAS"
        )
    for campo, valor in cambios.items():
        setattr(evento, campo, valor)
    await db.commit()
    return evento
