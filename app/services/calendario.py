"""En qué fase va un ciclo hoy, según las duraciones cargadas en el perfil del cultivo."""

from dataclasses import dataclass
from datetime import date, timedelta

from app.core.catalogos import fases_del_ciclo
from app.models.entities import Ciclo
from app.models.siembra import Siembra
from app.utils.fechas import a_dia


@dataclass(frozen=True)
class Avance:
    fase_actual: str | None
    fecha_fin_planeada: date | None
    fases_planeadas: int
    aviso: str | None


def avance_del_ciclo(siembra: Siembra, ciclo: Ciclo, hoy: date) -> Avance:
    validas = fases_del_ciclo(siembra.cultivo.tipo_ciclo, ciclo.tipo or "levante")
    fases = [f for f in siembra.cultivo.fases if f.fase in validas]
    if not fases:
        return Avance(None, None, 0, "El perfil del cultivo aún no tiene fases cargadas.")
    if ciclo.fecha_inicio is None:
        return Avance(None, None, len(fases), "El ciclo aún no inicia.")
    cursor = a_dia(ciclo.fecha_inicio)
    assert cursor is not None
    actual: str | None = None
    for fase in fases:
        if fase.dias_estimados is None:
            return Avance(None, None, len(fases), "Faltan los días estimados de las fases.")
        fin = cursor + timedelta(days=fase.dias_estimados)
        if actual is None and hoy < fin:
            actual = fase.fase
        cursor = fin
    return Avance(actual or fases[-1].fase, cursor, len(fases), None)
