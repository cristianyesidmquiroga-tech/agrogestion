"""Avisos de riesgo: cruzan la fase actual de cada ciclo con los riesgos críticos del perfil."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Usuario
from app.models.riesgo import CultivoRiesgo, Riesgo
from app.models.siembra import Siembra
from app.schemas.inicio import AvisoRiesgo, AvisosSalida
from app.services import calendario
from app.services.acceso_service import ids_fincas

FASES_LEGIBLES = {
    "preparacion": "preparación del terreno",
    "siembra": "siembra",
    "mantenimiento": "mantenimiento",
    "cosecha": "cosecha",
    "poscosecha": "poscosecha",
    "renovacion": "renovación",
}


async def avisos(db: AsyncSession, usuario: Usuario, hoy: date | None = None) -> AvisosSalida:
    hoy = hoy or date.today()
    siembras = await db.scalars(
        select(Siembra).where(
            Siembra.finca_id.in_(await ids_fincas(db, usuario)), Siembra.estado == "en_curso"
        )
    )
    salida: list[AvisoRiesgo] = []
    sin_calendario = 0
    for siembra in siembras:
        for ciclo in (c for c in siembra.ciclos if c.estado == "abierto"):
            avance = calendario.avance_del_ciclo(siembra, ciclo, hoy)
            if avance.fase_actual is None:
                sin_calendario += 1
                continue
            filas = await db.execute(
                select(CultivoRiesgo, Riesgo)
                .join(Riesgo, Riesgo.id == CultivoRiesgo.riesgo_id)
                .where(
                    CultivoRiesgo.cultivo_id == siembra.cultivo_id,
                    CultivoRiesgo.fase_critica == avance.fase_actual,
                )
                .order_by(Riesgo.nombre)
            )
            for cr, riesgo in filas:
                fase = FASES_LEGIBLES.get(avance.fase_actual, avance.fase_actual)
                salida.append(
                    AvisoRiesgo(
                        siembra_id=siembra.id,
                        ciclo_id=ciclo.id,
                        cultivo=siembra.cultivo.nombre,
                        fase=avance.fase_actual,
                        riesgo=riesgo.nombre,
                        susceptibilidad=cr.susceptibilidad,
                        medidas=cr.medidas,
                        por_validar=cr.por_validar,
                        texto=(
                            f"Su {siembra.cultivo.nombre} está en la fase de {fase}. "
                            f"El riesgo de {riesgo.nombre.lower()} es "
                            f"{cr.susceptibilidad} en esta fase."
                        ),
                    )
                )
    aviso = None
    if sin_calendario:
        aviso = (
            "Falta cargar la duración de las fases para calcular avisos "
            f"en {sin_calendario} ciclo(s)."
        )
    return AvisosSalida(avisos=salida, siembras_sin_calendario=sin_calendario, aviso=aviso)
