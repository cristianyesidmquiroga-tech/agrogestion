"""Inicio de sesión: mismo mensaje para cualquier fallo y bloqueo temporal tras varios intentos."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import claves
from app.core.config import get_settings
from app.core.contexto import UsuarioActual
from app.core.exceptions import LimiteSuperado, NoAutenticado
from app.models.usuario import IntentoAcceso, Usuario
from app.schemas.acceso import PerfilSalida, PermisoSalida
from app.services.acceso_service import ids_fincas

settings = get_settings()


async def _fallos_recientes(db: AsyncSession, correo: str) -> int:
    desde = datetime.now(UTC) - timedelta(minutes=settings.minutos_bloqueo)
    total = await db.scalar(
        select(func.count())
        .select_from(IntentoAcceso)
        .where(
            IntentoAcceso.correo == correo,
            IntentoAcceso.exitoso.is_(False),
            IntentoAcceso.creado_en >= desde,
        )
    )
    return int(total or 0)


async def _registrar(db: AsyncSession, correo: str, exitoso: bool) -> None:
    db.add(IntentoAcceso(correo=correo, exitoso=exitoso))
    await db.commit()


async def iniciar_sesion(db: AsyncSession, correo: str, clave: str) -> Usuario:
    correo = correo.strip().lower()[:160]
    if await _fallos_recientes(db, correo) >= settings.intentos_maximos:
        raise LimiteSuperado(
            f"Demasiados intentos. Intente de nuevo en {settings.minutos_bloqueo} minutos.",
            "DEMASIADOS_INTENTOS",
        )
    usuario = await db.scalar(select(Usuario).where(Usuario.correo == correo))
    valido = usuario is not None and usuario.activo and claves.verificar(clave, usuario.clave_hash)
    if usuario is None:
        claves.gastar_el_mismo_tiempo(clave)
    if not valido or usuario is None:
        await _registrar(db, correo, False)
        raise NoAutenticado("Correo o contraseña incorrectos.", "CREDENCIALES_INVALIDAS")
    usuario.ultimo_acceso = datetime.now(UTC)
    await _registrar(db, correo, True)
    return usuario


async def perfil(
    db: AsyncSession, actual: UsuarioActual, permisos: list[PermisoSalida]
) -> PerfilSalida:
    usuario = await db.get(Usuario, actual.id)
    if usuario is None:
        raise NoAutenticado("Su sesión venció o no es válida. Inicie sesión de nuevo.")
    return PerfilSalida(
        id=usuario.id,
        nombre=usuario.nombre,
        correo=usuario.correo,
        rol=usuario.rol,
        fincas=await ids_fincas(db, actual),
        permisos=permisos,
    )
