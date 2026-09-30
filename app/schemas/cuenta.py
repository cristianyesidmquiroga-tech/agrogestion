import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import Entrada, Salida


class TerminoSalida(Salida):
    id: uuid.UUID
    termino: str
    explicacion: str
    categoria: str


class PoliticaSalida(BaseModel):
    version: str
    estado: str
    datos_que_usamos: list[str]
    para_que: list[str]
    sus_derechos: list[str]


class ConsentimientoEntrada(Entrada):
    version_politica: str
    acepta_tratamiento: bool
    acepta_transferencia_ia: bool = False


class ConsentimientoSalida(Salida):
    version_politica: str
    aceptado_en: datetime
    acepta_transferencia_ia: bool
