"""Inicio de sesión: el único endpoint de datos sin candado."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.etiquetas import ACCESO
from app.core.permisos import permisos_del_rol
from app.core.security import Autenticado, crear_token
from app.routers.dependencias import BD
from app.schemas.acceso import PerfilSalida, PermisoSalida, TokenSalida
from app.schemas.common import ErrorRespuesta
from app.services import autenticacion_service as servicio

router = APIRouter(prefix="/auth", tags=[ACCESO])
settings = get_settings()


@router.post(
    "/login",
    response_model=TokenSalida,
    summary="Iniciar sesión y obtener el token",
    description=(
        "Recibe un formulario (no JSON) con `username` (el correo) y `password`. "
        "Devuelve el token del perfil con el que entró: cópielo y péguelo en Authorize."
    ),
    responses={429: {"model": ErrorRespuesta, "description": "Demasiados intentos fallidos."}},
)
async def login(db: BD, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenSalida:
    usuario = await servicio.iniciar_sesion(db, form.username, form.password)
    return TokenSalida(
        access_token=crear_token(usuario.id),
        token_type="bearer",  # noqa: S106
        expires_in=settings.access_token_expire_minutes * 60,
        rol=usuario.rol,
        nombre=usuario.nombre,
    )


@router.get(
    "/me", response_model=PerfilSalida, summary="Quién soy y qué puedo usar con este perfil"
)
async def me(db: BD, usuario: Autenticado, request: Request) -> PerfilSalida:
    permisos = [PermisoSalida(**p) for p in permisos_del_rol(request.app.routes, usuario.rol)]
    return await servicio.perfil(db, usuario, permisos)
