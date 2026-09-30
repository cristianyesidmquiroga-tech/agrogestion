"""Pantalla de inicio: lo que el usuario necesita ver hoy con los datos que ya existen."""

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.contexto import UsuarioActual
from app.models.finca import Lote
from app.models.riesgo import EventoAdverso, Riesgo
from app.models.siembra import Siembra
from app.schemas.inicio import EventoReciente, InicioSalida
from app.services import aviso_service
from app.services.acceso_service import ids_fincas


async def resumen(
    db: AsyncSession, usuario: UsuarioActual, hoy: date | None = None
) -> InicioSalida:
    hoy = hoy or date.today()
    fincas = await ids_fincas(db, usuario)
    conteo_estados = await db.execute(
        select(Siembra.estado, func.count())
        .where(Siembra.finca_id.in_(fincas))
        .group_by(Siembra.estado)
    )
    por_estado: dict[str, int] = {estado: int(n) for estado, n in conteo_estados.all()}
    lotes = (
        await db.scalar(select(func.count()).select_from(Lote).where(Lote.finca_id.in_(fincas)))
        or 0
    )
    filas = await db.execute(
        select(EventoAdverso, Riesgo)
        .join(Riesgo, Riesgo.id == EventoAdverso.riesgo_id)
        .where(EventoAdverso.finca_id.in_(fincas), EventoAdverso.inicio >= hoy - timedelta(days=30))
        .order_by(EventoAdverso.inicio.desc())
        .limit(3)
    )
    eventos = [
        EventoReciente(id=e.id, riesgo=r.nombre, severidad=e.severidad, inicio=e.inicio)
        for e, r in filas
    ]
    pasos: list[str] = []
    if usuario.rol == "experto":
        pass
    elif not fincas:
        pasos.append("Pida que le asignen una finca para empezar.")
    elif not lotes:
        pasos.append("Registre los lotes de su finca.")
    if fincas and lotes and not sum(por_estado.values()):
        pasos.append("Planee su primera siembra.")
    avisos = (await aviso_service.avisos(db, usuario, hoy)).avisos[:3]
    return InicioSalida(
        fincas=len(fincas),
        siembras_en_curso=int(por_estado.get("en_curso", 0)),
        siembras_planeadas=int(por_estado.get("planeada", 0)),
        avisos=avisos,
        eventos_recientes=eventos,
        primeros_pasos=pasos,
    )
