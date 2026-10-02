"""Noticias por región y cultivo. Todas vencen solas: el usuario siempre ve información actual."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import ColumnElement, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ReglaNegocio
from app.models.entities import Finca, FincaUsuario, Usuario
from app.models.noticia import Noticia
from app.models.siembra import Siembra
from app.schemas.noticia import NoticiaCrear
from app.services import cultivo_service

settings = get_settings()


async def _regiones_del_usuario(db: AsyncSession, usuario: Usuario) -> set[str]:
    filas = await db.execute(
        select(Finca.municipio_dane, Finca.departamento_dane)
        .join(FincaUsuario, FincaUsuario.finca_id == Finca.id)
        .where(FincaUsuario.usuario_id == usuario.id)
    )
    regiones: set[str] = set()
    for municipio, departamento in filas:
        regiones.update((municipio, departamento))
    return regiones


async def _cultivos_del_usuario(db: AsyncSession, usuario: Usuario) -> set[uuid.UUID]:
    filas = await db.scalars(
        select(Siembra.cultivo_id)
        .join(FincaUsuario, FincaUsuario.finca_id == Siembra.finca_id)
        .where(FincaUsuario.usuario_id == usuario.id, Siembra.estado.in_(("planeada", "en_curso")))
    )
    return set(filas)


async def listar(
    db: AsyncSession,
    usuario: Usuario,
    region: str | None,
    cultivo_id: uuid.UUID | None,
    skip: int,
    limit: int,
) -> tuple[list[Noticia], int]:
    filtros: list[ColumnElement[bool]] = [Noticia.vigente_hasta > datetime.now(UTC)]
    regiones = {region} if region else await _regiones_del_usuario(db, usuario)
    filtros.append(or_(Noticia.region_dane.is_(None), Noticia.region_dane.in_(regiones)))
    cultivos = {cultivo_id} if cultivo_id else await _cultivos_del_usuario(db, usuario)
    filtros.append(or_(Noticia.cultivo_id.is_(None), Noticia.cultivo_id.in_(cultivos)))
    total = await db.scalar(select(func.count()).select_from(Noticia).where(*filtros)) or 0
    filas = await db.scalars(
        select(Noticia).where(*filtros).order_by(Noticia.publicada.desc()).offset(skip).limit(limit)
    )
    return list(filas), total


async def crear(db: AsyncSession, datos: NoticiaCrear, usuario_id: uuid.UUID) -> Noticia:
    if datos.cultivo_id:
        await cultivo_service.obtener(db, datos.cultivo_id)
    publicada = datos.publicada or datetime.now(UTC)
    vence = datos.vigente_hasta or publicada + timedelta(days=settings.noticias_dias_vigencia)
    if vence <= publicada:
        raise ReglaNegocio(
            "La noticia debe vencer después de publicarse.", "NOTICIA_FECHAS_INVALIDAS"
        )
    noticia = Noticia(
        titulo=datos.titulo,
        resumen=datos.resumen,
        enlace=datos.enlace,
        fuente=datos.fuente,
        region_dane=datos.region_dane,
        cultivo_id=datos.cultivo_id,
        publicada=publicada,
        vigente_hasta=vence,
        creado_por=usuario_id,
    )
    db.add(noticia)
    await db.commit()
    return noticia


async def borrar_vencidas(db: AsyncSession) -> int:
    resultado = await db.execute(delete(Noticia).where(Noticia.vigente_hasta <= datetime.now(UTC)))
    await db.commit()
    return int(getattr(resultado, "rowcount", 0) or 0)
