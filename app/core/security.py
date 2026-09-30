"""Verificación del token y roles. El inicio de sesión lo completa el módulo de acceso."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.contexto import UsuarioActual
from app.core.database import get_db
from app.core.exceptions import NoAutenticado, SinPermiso
from app.models.usuario import Usuario

settings = get_settings()
oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login", auto_error=False)


def crear_token(usuario_id: uuid.UUID, minutos: int | None = None) -> str:
    ahora = datetime.now(UTC)
    vence = ahora + timedelta(minutes=minutos or settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(usuario_id), "iat": ahora, "exp": vence},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


async def get_usuario_actual(
    token: Annotated[str | None, Depends(oauth2)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UsuarioActual:
    sesion_invalida = NoAutenticado("Su sesión venció o no es válida. Inicie sesión de nuevo.")
    if not token:
        raise NoAutenticado("Inicie sesión para continuar.")
    try:
        datos = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        usuario_id = uuid.UUID(str(datos["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise sesion_invalida from None
    usuario = await db.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        raise sesion_invalida
    return UsuarioActual(id=usuario.id, rol=usuario.rol)


class RequiereRol:
    """Dependencia que deja pasar solo a los roles indicados."""

    def __init__(self, *roles: str) -> None:
        self.roles = roles

    async def __call__(
        self, usuario: Annotated[UsuarioActual, Depends(get_usuario_actual)]
    ) -> UsuarioActual:
        if usuario.rol not in self.roles:
            raise SinPermiso("No tiene permiso para esta acción.")
        return usuario


Autenticado = Annotated[UsuarioActual, Depends(get_usuario_actual)]
EscribeProduccion = Annotated[UsuarioActual, Depends(RequiereRol("admin", "agricultor"))]
LeeProduccion = Annotated[UsuarioActual, Depends(RequiereRol("admin", "agricultor", "contador"))]
SoloAdmin = Annotated[UsuarioActual, Depends(RequiereRol("admin"))]
