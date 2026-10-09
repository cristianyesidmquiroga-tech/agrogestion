import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.auth import COMMON_PASSWORDS
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


class CambioClaveEntrada(Entrada):
    clave_actual: str
    clave_nueva: str = Field(min_length=10)

    @field_validator("clave_nueva")
    @classmethod
    def rechazar_clave_comun(cls, valor: str) -> str:
        if valor.lower() in COMMON_PASSWORDS:
            raise ValueError("La contraseña es demasiado común")
        return valor
