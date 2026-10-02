from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.models import Finca, FincaUsuario, Lote
from app.schemas.land import FincaCreate, LoteCreate


async def create_finca(db: AsyncSession, user_id: UUID, data: FincaCreate) -> Finca:
    finca = Finca(
        nombre=data.nombre,
        departamento_dane=data.departamento_dane,
        municipio_dane=data.municipio_dane,
        area_ha=data.area_ha,
        creado_por=user_id,
    )
    db.add(finca)
    await db.flush()
    db.add(FincaUsuario(finca_id=finca.id, usuario_id=user_id))
    await db.commit()
    await db.refresh(finca)
    return finca


async def user_finca(db: AsyncSession, user_id: UUID, finca_id: UUID) -> Finca:
    finca = await db.scalar(
        select(Finca)
        .join(FincaUsuario)
        .where(Finca.id == finca_id, FincaUsuario.usuario_id == user_id)
    )
    if not finca:
        raise AppError(
            404, "FINCA_NO_ENCONTRADA", "La finca no existe o no está asignada al usuario."
        )
    return finca


async def create_lote(db: AsyncSession, user_id: UUID, finca_id: UUID, data: LoteCreate) -> Lote:
    await user_finca(db, user_id, finca_id)
    lote = Lote(
        finca_id=finca_id, nombre=data.nombre, area=data.area, notas=data.notas, creado_por=user_id
    )
    db.add(lote)
    await db.commit()
    await db.refresh(lote)
    return lote
