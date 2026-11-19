import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, NoEncontrado
from app.core.security import hash_password
from app.models import Cosecha, Finca, FincaUsuario, Gasto, Ingreso, Siembra, Usuario
from app.schemas.administracion import FincaDeUsuario, UsuarioDetalle, UsuarioResumen
from app.schemas.auth import UsuarioCreate


async def create_user(db: AsyncSession, data: UsuarioCreate) -> Usuario:
    if await db.scalar(select(Usuario).where(Usuario.email == data.email.lower())):
        raise AppError(409, "EMAIL_EN_USO", "El correo electrónico ya está registrado.")
    user = Usuario(
        email=data.email.lower(),
        nombre=data.nombre,
        password_hash=hash_password(data.password),
        rol=data.rol,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _conteos(db: AsyncSession, consulta: Select[Any]) -> dict[Any, int]:
    return {clave: int(n) for clave, n in (await db.execute(consulta)).all()}


async def _por_finca(
    db: AsyncSession, modelo: Any, campo: Any, ids: list[Any], activo: str
) -> dict[Any, Decimal]:
    consulta = (
        select(modelo.finca_id, func.coalesce(func.sum(campo), 0))
        .where(modelo.finca_id.in_(ids), modelo.estado == activo)
        .group_by(modelo.finca_id)
    )
    return {finca: Decimal(valor) for finca, valor in (await db.execute(consulta)).all()}


async def listar_usuarios(
    db: AsyncSession, q: str | None, rol: str | None, activo: bool | None, skip: int, limit: int
) -> tuple[list[UsuarioResumen], int]:
    filtros = []
    if q:
        patron = f"%{q}%"
        filtros.append(or_(Usuario.nombre.ilike(patron), Usuario.email.ilike(patron)))
    if rol:
        filtros.append(Usuario.rol == rol)
    if activo is not None:
        filtros.append(Usuario.activo == activo)
    total = await db.scalar(select(func.count()).select_from(Usuario).where(*filtros)) or 0
    filas = list(
        await db.scalars(
            select(Usuario)
            .where(*filtros)
            .order_by(Usuario.nombre, Usuario.id)
            .offset(skip)
            .limit(limit)
        )
    )
    ids = [u.id for u in filas]
    fincas = await _conteos(
        db,
        select(FincaUsuario.usuario_id, func.count())
        .where(FincaUsuario.usuario_id.in_(ids))
        .group_by(FincaUsuario.usuario_id),
    )
    siembras = await _conteos(
        db,
        select(FincaUsuario.usuario_id, func.count(Siembra.id))
        .join(Siembra, Siembra.finca_id == FincaUsuario.finca_id)
        .where(FincaUsuario.usuario_id.in_(ids))
        .group_by(FincaUsuario.usuario_id),
    )
    resumen = [
        UsuarioResumen(
            id=u.id,
            email=u.email,
            nombre=u.nombre,
            rol=u.rol,
            activo=u.activo,
            creado_en=u.creado_en,
            ultimo_acceso=u.ultimo_acceso,
            municipio_dane=u.municipio_dane,
            fincas=fincas.get(u.id, 0),
            siembras=siembras.get(u.id, 0),
        )
        for u in filas
    ]
    return resumen, total


async def detalle_usuario(db: AsyncSession, usuario_id: uuid.UUID) -> UsuarioDetalle:
    usuario = await db.get(Usuario, usuario_id)
    if usuario is None:
        raise NoEncontrado("No encontramos ese usuario.", "USUARIO_NO_ENCONTRADO")
    fincas = list(
        await db.scalars(
            select(Finca)
            .join(FincaUsuario, FincaUsuario.finca_id == Finca.id)
            .where(FincaUsuario.usuario_id == usuario_id)
            .order_by(Finca.nombre)
        )
    )
    ids = [f.id for f in fincas]
    siembras = await _conteos(
        db,
        select(Siembra.finca_id, func.count())
        .where(Siembra.finca_id.in_(ids))
        .group_by(Siembra.finca_id),
    )
    cosechas = await _conteos(
        db,
        select(Cosecha.finca_id, func.count())
        .where(Cosecha.finca_id.in_(ids), Cosecha.estado == "activa")
        .group_by(Cosecha.finca_id),
    )
    gastos = await _por_finca(db, Gasto, Gasto.monto, ids, "activo")
    ingresos = await _por_finca(db, Ingreso, Ingreso.total, ids, "activo")
    detalle = [
        FincaDeUsuario(
            id=f.id,
            nombre=f.nombre,
            departamento_dane=f.departamento_dane,
            municipio_dane=f.municipio_dane,
            area_ha=f.area_ha,
            siembras=siembras.get(f.id, 0),
            cosechas=cosechas.get(f.id, 0),
            gastos=gastos.get(f.id, Decimal(0)),
            ingresos=ingresos.get(f.id, Decimal(0)),
        )
        for f in fincas
    ]
    ahora = datetime.now(UTC)
    bloqueado_hasta = usuario.bloqueado_hasta
    if bloqueado_hasta is not None and bloqueado_hasta.tzinfo is None:
        bloqueado_hasta = bloqueado_hasta.replace(tzinfo=UTC)
    return UsuarioDetalle(
        id=usuario.id,
        email=usuario.email,
        nombre=usuario.nombre,
        rol=usuario.rol,
        activo=usuario.activo,
        creado_en=usuario.creado_en,
        ultimo_acceso=usuario.ultimo_acceso,
        municipio_dane=usuario.municipio_dane,
        fincas=len(fincas),
        siembras=sum(d.siembras for d in detalle),
        bloqueado=bloqueado_hasta is not None and bloqueado_hasta > ahora,
        cosechas=sum(d.cosechas for d in detalle),
        gastos=sum((d.gastos for d in detalle), Decimal(0)),
        ingresos=sum((d.ingresos for d in detalle), Decimal(0)),
        detalle_fincas=detalle,
    )
