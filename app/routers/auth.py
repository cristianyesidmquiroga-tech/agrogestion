from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.security import create_access_token, verify_password
from app.dependencies import current_user
from app.models import Usuario
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await db.scalar(select(Usuario).where(Usuario.email == data.email.lower()))
    now = datetime.now(UTC)
    valid = user is not None and (user.bloqueado_hasta is None or user.bloqueado_hasta <= now)
    if user and valid and verify_password(data.password, user.password_hash):
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        await db.commit()
        return TokenResponse(access_token=create_access_token(user.id))
    if user and valid:
        user.intentos_fallidos += 1
        settings = get_settings()
        if user.intentos_fallidos >= settings.login_max_attempts:
            user.bloqueado_hasta = now + timedelta(minutes=settings.login_lock_minutes)
        await db.commit()
    raise AppError(401, "CREDENCIALES_INVALIDAS", "El correo o la contraseña no son válidos.")


@router.get("/me", response_model=UsuarioResponse)
async def me(user: Usuario = Depends(current_user)) -> Usuario:
    return user
