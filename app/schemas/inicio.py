import uuid
from datetime import date

from pydantic import BaseModel

from app.core.catalogos import Severidad, Susceptibilidad
from app.schemas.common import Decimal2, Indicador


class AvisoRiesgo(BaseModel):
    siembra_id: uuid.UUID
    ciclo_id: uuid.UUID
    cultivo: str
    fase: str
    riesgo: str
    susceptibilidad: Susceptibilidad
    medidas: str | None
    por_validar: bool
    texto: str


class AvisosSalida(BaseModel):
    avisos: list[AvisoRiesgo]
    siembras_sin_calendario: int
    aviso: str | None = None


class EventoReciente(BaseModel):
    id: uuid.UUID
    riesgo: str
    severidad: Severidad
    inicio: date


class InicioSalida(BaseModel):
    fincas: int
    siembras_en_curso: int
    siembras_planeadas: int
    avisos: list[AvisoRiesgo]
    eventos_recientes: list[EventoReciente]
    primeros_pasos: list[str]


class ReporteDisponible(BaseModel):
    id: str
    titulo: str
    descripcion: str
    disponible: bool
    motivo: str | None = None
    roles: list[str]


class IndiceSiembra(BaseModel):
    siembra_id: uuid.UUID
    cultivo: str
    lote_id: uuid.UUID
    fecha_conteo: date | None
    indicadores: list[Indicador]
    aviso: str | None = None


class ReporteIndices(BaseModel):
    siembras: list[IndiceSiembra]


class CicloCronograma(BaseModel):
    siembra_id: uuid.UUID
    ciclo_id: uuid.UUID
    cultivo: str
    tipo: str
    fecha_inicio: date | None
    fase_actual: str | None
    fases_planeadas: int
    fecha_fin_planeada: date | None
    aviso: str | None = None


class ReporteCronograma(BaseModel):
    ciclos: list[CicloCronograma]


class EventosPorTipo(BaseModel):
    tipo: str
    cantidad: int
    perdida_estimada: Decimal2
    perdida_promedio_pct: float | None


class ReporteEventos(BaseModel):
    desde: date | None
    hasta: date | None
    total: int
    perdida_estimada_total: Decimal2
    por_tipo: list[EventosPorTipo]
    por_severidad: dict[str, int]
    aviso: str | None = None
