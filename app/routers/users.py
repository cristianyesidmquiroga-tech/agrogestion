import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.etiquetas import USUARIOS
from app.dependencies import SoloAdmin, require_role
from app.models import Usuario
from app.routers.dependencias import BD, Pagina, armar_pagina
from app.schemas.administracion import UsuarioDetalle, UsuarioResumen
from app.schemas.auth import UsuarioCreate, UsuarioResponse
from app.schemas.common import Page
from app.services import users as servicio
from app.services.users import create_user

router = APIRouter(prefix="/usuarios", tags=[USUARIOS])


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_role("admin")),
) -> Usuario:
    return await create_user(db, data)


@router.get("", response_model=Page[UsuarioResumen], summary="Perfiles de los usuarios")
async def listar(
    db: BD,
    _: SoloAdmin,
    pag: Pagina,
    q: Annotated[str | None, Query(max_length=80, description="Texto en nombre o correo")] = None,
    rol: Annotated[Literal["admin", "agricultor", "contador", "experto"] | None, Query()] = None,
    activo: bool | None = None,
) -> Page[UsuarioResumen]:
    items, total = await servicio.listar_usuarios(db, q, rol, activo, pag.skip, pag.limit)
    return armar_pagina(items, total, pag)


@router.get("/{usuario_id}", response_model=UsuarioDetalle, summary="Perfil de un usuario")
async def detalle(db: BD, _: SoloAdmin, usuario_id: uuid.UUID) -> UsuarioDetalle:
    return await servicio.detalle_usuario(db, usuario_id)
