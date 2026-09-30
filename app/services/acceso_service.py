"""Aislamiento entre fincas: cada usuario solo ve las que tiene asignadas."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.contexto import UsuarioActual
from app.core.exceptions import NoEncontrado
from app.models.finca import Finca, FincaUsuario


async def ids_fincas(db: AsyncSession, usuario: UsuarioActual) -> list[uuid.UUID]:
    filas = await db.scalars(
        select(FincaUsuario.finca_id).where(FincaUsuario.usuario_id == usuario.id)
    )
    return list(filas)


async def exigir_finca(
    db: AsyncSession,
    usuario: UsuarioActual,
    finca_id: uuid.UUID,
    mensaje: str = "No encontramos esa finca.",
    codigo: str = "FINCA_NO_ENCONTRADA",
) -> Finca:
    """Devuelve la finca si el usuario la tiene asignada; si no, responde como si no existiera."""
    consulta = (
        select(Finca)
        .join(FincaUsuario, FincaUsuario.finca_id == Finca.id)
        .where(Finca.id == finca_id, FincaUsuario.usuario_id == usuario.id)
    )
    finca = await db.scalar(consulta)
    if finca is None:
        raise NoEncontrado(mensaje, codigo)
    return finca
