from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import current_user
from app.models import Finca, FincaUsuario, Lote, Usuario
from app.schemas.land import FincaCreate, FincaResponse, LoteCreate, LoteResponse
from app.services.lands import create_finca, create_lote

router = APIRouter(prefix="/fincas", tags=["fincas"])


@router.post("", response_model=FincaResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: FincaCreate, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> Finca:
    return await create_finca(db, user.id, data)


@router.get("", response_model=list[FincaResponse])
async def list_owned(
    db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[Finca]:
    result = await db.scalars(
        select(Finca).join(FincaUsuario).where(FincaUsuario.usuario_id == user.id)
    )
    return list(result)


@router.post("/{finca_id}/lotes", response_model=LoteResponse, status_code=status.HTTP_201_CREATED)
async def create_lot(
    finca_id: UUID,
    data: LoteCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Lote:
    return await create_lote(db, user.id, finca_id, data)


@router.get("/{finca_id}/lotes", response_model=list[LoteResponse])
async def list_lots(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[Lote]:
    from app.services.lands import user_finca

    await user_finca(db, user.id, finca_id)
    result = await db.scalars(select(Lote).where(Lote.finca_id == finca_id))
    return list(result)
