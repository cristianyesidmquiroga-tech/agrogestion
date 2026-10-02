"""Listas cerradas de valores que comparten modelos, esquemas y reglas."""

from typing import Literal

RolUsuario = Literal["admin", "agricultor", "contador", "experto"]
TipoCiclo = Literal["transitorio", "semipermanente", "permanente", "forestal"]
UnidadConteo = Literal["planta", "area"]
TipoRenovacion = Literal["zoca", "soca", "poda", "resiembra"]
PagoCosecha = Literal["por_kilo", "por_jornal", "por_destajo"]
Fase = Literal["preparacion", "siembra", "mantenimiento", "cosecha", "poscosecha", "renovacion"]
MetodoPropagacion = Literal[
    "semilla", "esqueje", "estaca", "injerto", "hijuelo", "acodo", "in_vitro"
]
BaseDosis = Literal["planta", "hectarea"]
EstadoSiembra = Literal["planeada", "en_curso", "cerrada", "cancelada"]
TipoCicloSiembra = Literal["levante", "produccion", "renovacion"]
EstadoCiclo = Literal["planeado", "abierto", "cerrado"]
TipoRiesgo = Literal["clima", "plaga", "enfermedad", "otro"]
AplicaA = Literal["cultivo", "animal", "ambos"]
Susceptibilidad = Literal["baja", "media", "alta"]
Severidad = Literal["leve", "moderada", "severa"]
TipoProblema = Literal["plaga", "enfermedad", "deficiencia", "clima", "otro"]
EstadoConocimiento = Literal["borrador", "validado", "retirado"]
TipoManejo = Literal["prevencion", "cultural", "quimico", "veterinario"]
Coincidencia = Literal["alta", "media", "baja"]
ValorRetroalimentacion = Literal["sirvio", "no_sirvio", "equivocado"]
EstadoIndicador = Literal["bien", "atencion", "alerta", "informativo"]

FASES_TRANSITORIO = ("preparacion", "siembra", "mantenimiento", "cosecha", "poscosecha")
FASES_CICLO: dict[str, tuple[str, ...]] = {
    "levante": ("preparacion", "siembra", "mantenimiento"),
    "produccion": ("mantenimiento", "cosecha", "poscosecha"),
    "renovacion": ("renovacion", "siembra", "mantenimiento"),
}


def fases_del_ciclo(tipo_ciclo_cultivo: str, tipo_ciclo: str) -> tuple[str, ...]:
    """Fases válidas para un ciclo según el tipo de cultivo."""
    if tipo_ciclo_cultivo == "transitorio":
        return FASES_TRANSITORIO
    return FASES_CICLO.get(tipo_ciclo, ())
