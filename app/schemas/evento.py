import uuid
from datetime import date
from typing import Self

from pydantic import Field, model_validator

from app.core.catalogos import Severidad
from app.schemas.common import Decimal2, Entrada, Salida


class EventoCrear(Entrada):
    finca_id: uuid.UUID
    riesgo_id: uuid.UUID
    siembra_id: uuid.UUID | None = None
    ciclo_id: uuid.UUID | None = None
    inicio: date
    fin: date | None = None
    severidad: Severidad
    area_afectada: Decimal2 | None = Field(default=None, ge=0, max_digits=10, decimal_places=4)
    perdida_pct: Decimal2 | None = Field(default=None, ge=0, le=100, max_digits=5, decimal_places=2)
    perdida_estimada: Decimal2 | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    notas: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def _fechas(self) -> Self:
        if self.fin is not None and self.fin < self.inicio:
            raise ValueError("La fecha final no puede ser anterior a la inicial.")
        return self


class EventoActualizar(Entrada):
    fin: date | None = None
    severidad: Severidad | None = None
    area_afectada: Decimal2 | None = Field(default=None, ge=0, max_digits=10, decimal_places=4)
    perdida_pct: Decimal2 | None = Field(default=None, ge=0, le=100, max_digits=5, decimal_places=2)
    perdida_estimada: Decimal2 | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    notas: str | None = Field(default=None, max_length=2000)


class EventoSalida(Salida):
    id: uuid.UUID
    finca_id: uuid.UUID
    riesgo_id: uuid.UUID
    siembra_id: uuid.UUID | None
    ciclo_id: uuid.UUID | None
    inicio: date
    fin: date | None
    severidad: str
    area_afectada: Decimal2 | None
    perdida_pct: Decimal2 | None
    perdida_estimada: Decimal2 | None
    notas: str | None
