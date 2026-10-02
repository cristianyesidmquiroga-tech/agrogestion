"""Base de conocimiento: solo lo validado llega al usuario; un experto revisa cada entrada."""

import uuid

from sqlalchemy import ColumnElement, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NoEncontrado, ReglaNegocio
from app.models.conocimiento import Fuente, Manejo, ProblemaSanitario, Sintoma, Validacion
from app.models.entities import Usuario
from app.schemas.conocimiento import CambiarEstado, FuenteCrear, ProblemaCrear
from app.services import cultivo_service

REVISORES = ("admin", "experto")

TRANSICIONES = {
    "borrador": ("validado", "retirado"),
    "validado": ("retirado",),
    "retirado": ("borrador",),
}


def _revisa(usuario: Usuario) -> bool:
    return usuario.rol in REVISORES


async def listar(
    db: AsyncSession,
    usuario: Usuario,
    q: str | None,
    cultivo_id: uuid.UUID | None,
    tipo: str | None,
    estado: str | None,
    skip: int,
    limit: int,
) -> tuple[list[ProblemaSanitario], int]:
    filtros: list[ColumnElement[bool]] = []
    if not _revisa(usuario):
        filtros.append(ProblemaSanitario.estado == "validado")
    elif estado:
        filtros.append(ProblemaSanitario.estado == estado)
    if cultivo_id:
        filtros.append(ProblemaSanitario.cultivo_id == cultivo_id)
    if tipo:
        filtros.append(ProblemaSanitario.tipo == tipo)
    if q:
        patron = f"%{q}%"
        con_sintoma = exists().where(
            Sintoma.problema_id == ProblemaSanitario.id, Sintoma.descripcion.ilike(patron)
        )
        filtros.append(or_(ProblemaSanitario.nombre.ilike(patron), con_sintoma))
    total = (
        await db.scalar(select(func.count()).select_from(ProblemaSanitario).where(*filtros)) or 0
    )
    filas = await db.scalars(
        select(ProblemaSanitario)
        .where(*filtros)
        .order_by(ProblemaSanitario.nombre)
        .offset(skip)
        .limit(limit)
    )
    return list(filas), total


async def obtener(db: AsyncSession, usuario: Usuario, problema_id: uuid.UUID) -> ProblemaSanitario:
    problema = await db.get(ProblemaSanitario, problema_id)
    if problema is None or (not _revisa(usuario) and problema.estado != "validado"):
        raise NoEncontrado("No encontramos esa ficha.", "PROBLEMA_NO_ENCONTRADO")
    return problema


async def _fuentes_existen(db: AsyncSession, ids: set[uuid.UUID]) -> None:
    if not ids:
        return
    existentes = set(await db.scalars(select(Fuente.id).where(Fuente.id.in_(ids))))
    if ids - existentes:
        raise NoEncontrado("Una de las fuentes no existe.", "FUENTE_NO_ENCONTRADA")


async def crear(db: AsyncSession, datos: ProblemaCrear, usuario_id: uuid.UUID) -> ProblemaSanitario:
    if datos.cultivo_id:
        await cultivo_service.obtener(db, datos.cultivo_id)
    await _fuentes_existen(db, {m.fuente_id for m in datos.manejos if m.fuente_id})
    problema = ProblemaSanitario(
        nombre=datos.nombre,
        tipo=datos.tipo,
        cultivo_id=datos.cultivo_id,
        causa=datos.causa,
        estado="borrador",
        creado_por=usuario_id,
    )
    problema.sintomas = [Sintoma(**s.model_dump()) for s in datos.sintomas]
    problema.manejos = [Manejo(**m.model_dump()) for m in datos.manejos]
    db.add(problema)
    await db.commit()
    await db.refresh(problema)
    return problema


async def cambiar_estado(
    db: AsyncSession, problema_id: uuid.UUID, datos: CambiarEstado, experto_id: uuid.UUID
) -> ProblemaSanitario:
    problema = await db.get(ProblemaSanitario, problema_id)
    if problema is None:
        raise NoEncontrado("No encontramos esa ficha.", "PROBLEMA_NO_ENCONTRADO")
    if datos.estado not in TRANSICIONES[problema.estado]:
        raise ReglaNegocio(
            f"Una ficha {problema.estado} no puede pasar a {datos.estado}.", "ESTADO_NO_PERMITIDO"
        )
    if datos.estado == "validado":
        if not problema.sintomas:
            raise ReglaNegocio(
                "Para validar, la ficha necesita al menos un síntoma.", "FICHA_INCOMPLETA"
            )
        if not problema.manejos or any(m.fuente_id is None for m in problema.manejos):
            raise ReglaNegocio(
                "Para validar, cada manejo debe tener su fuente.", "FICHA_SIN_FUENTE"
            )
    problema.estado = datos.estado
    db.add(
        Validacion(
            problema_id=problema.id,
            experto_id=experto_id,
            estado=datos.estado,
            observacion=datos.observacion,
            creado_por=experto_id,
        )
    )
    await db.commit()
    await db.refresh(problema, attribute_names=["validaciones"])
    return problema


async def listar_fuentes(db: AsyncSession) -> list[Fuente]:
    return list(await db.scalars(select(Fuente).order_by(Fuente.nombre)))


async def crear_fuente(db: AsyncSession, datos: FuenteCrear, usuario_id: uuid.UUID) -> Fuente:
    fuente = Fuente(**datos.model_dump(), creado_por=usuario_id)
    db.add(fuente)
    await db.commit()
    return fuente
