from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.security import decode_access_token
from app.models import Usuario

bearer = HTTPBearer(auto_error=False)


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    if not credentials:
        raise AppError(401, "NO_AUTENTICADO", "Debe autenticarse para continuar.")
    try:
        user_id: UUID = decode_access_token(credentials.credentials)
    except Exception as exc:
        raise AppError(401, "TOKEN_INVALIDO", "La autenticación no es válida.") from exc
    user = await db.scalar(select(Usuario).where(Usuario.id == user_id, Usuario.activo.is_(True)))
    if not user:
        raise AppError(401, "NO_AUTENTICADO", "Debe autenticarse para continuar.")
    return user


def require_role(*roles: str):  # type: ignore[no-untyped-def]
    async def dependency(user: Usuario = Depends(current_user)) -> Usuario:
        if user.rol not in roles:
            raise AppError(
                403, "PERMISO_DENEGADO", "No tiene permisos para realizar esta operación."
            )
        return user

    return dependency


async def idempotency_key(
    value: str | None = Header(default=None, alias="Idempotency-Key"),
) -> str | None:
    return value
