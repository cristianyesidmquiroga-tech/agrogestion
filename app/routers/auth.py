from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.etiquetas import ACCESO
from app.core.exceptions import AppError
from app.core.permisos import permisos_del_rol
from app.core.security import create_access_token, gastar_el_mismo_tiempo, verify_password
from app.dependencies import current_user
from app.models import Usuario
from app.schemas.auth import LoginRequest, PerfilResponse, PermisoResponse, TokenResponse
from app.services.acceso_service import ids_fincas

router = APIRouter(prefix="/auth", tags=[ACCESO])


def _bloqueado(user: Usuario, now: datetime) -> bool:
    hasta = user.bloqueado_hasta
    if hasta is None:
        return False
    return (hasta if hasta.tzinfo else hasta.replace(tzinfo=UTC)) > now


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión y obtener el token")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await db.scalar(select(Usuario).where(Usuario.email == data.email.lower()))
    now = datetime.now(UTC)
    settings = get_settings()
    valid = user is not None and user.activo and not _bloqueado(user, now)
    if user is None:
        gastar_el_mismo_tiempo(data.password)
    if user and valid and verify_password(data.password, user.password_hash):
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        user.ultimo_acceso = now
        await db.commit()
        return TokenResponse(
            access_token=create_access_token(user.id),
            expires_in=settings.jwt_expire_minutes * 60,
            rol=user.rol,
            nombre=user.nombre,
        )
    if user and valid:
        user.intentos_fallidos += 1
        if user.intentos_fallidos >= settings.login_max_attempts:
            user.bloqueado_hasta = now + timedelta(minutes=settings.login_lock_minutes)
        await db.commit()
    raise AppError(401, "CREDENCIALES_INVALIDAS", "El correo o la contraseña no son válidos.")


@router.get("/me", response_model=PerfilResponse, summary="Quién soy y qué puedo usar")
async def me(
    request: Request, user: Usuario = Depends(current_user), db: AsyncSession = Depends(get_db)
) -> PerfilResponse:
    permisos = permisos_del_rol(request.app.routes, user.rol)
    return PerfilResponse(
        id=user.id,
        email=user.email,
        nombre=user.nombre,
        rol=user.rol,
        activo=user.activo,
        fincas=await ids_fincas(db, user),
        permisos=[PermisoResponse(**p) for p in permisos],
    )
