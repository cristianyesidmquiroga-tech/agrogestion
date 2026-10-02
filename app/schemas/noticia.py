import uuid
from datetime import datetime

from pydantic import Field, field_validator

from app.schemas.common import Entrada, Salida


class NoticiaCrear(Entrada):
    titulo: str = Field(min_length=3, max_length=200)
    resumen: str = Field(min_length=3, max_length=400)
    enlace: str = Field(min_length=8, max_length=400, pattern=r"^https?://")
    fuente: str = Field(min_length=2, max_length=120)
    region_dane: str | None = None
    cultivo_id: uuid.UUID | None = None
    publicada: datetime | None = None
    vigente_hasta: datetime | None = None

    @field_validator("region_dane")
    @classmethod
    def _region(cls, valor: str | None) -> str | None:
        if valor is not None and not (valor.isdigit() and len(valor) in (2, 5)):
            raise ValueError("Use el código DANE del departamento (2 dígitos) o del municipio (5).")
        return valor


class NoticiaSalida(Salida):
    id: uuid.UUID
    titulo: str
    resumen: str
    enlace: str
    fuente: str
    region_dane: str | None
    cultivo_id: uuid.UUID | None
    publicada: datetime
    vigente_hasta: datetime
