from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.utils.dane import codigos_dane_validos


class FincaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    ubicacion: str | None = None
    departamento_dane: str | None = Field(default=None, pattern=r"^\d{2}$")
    municipio_dane: str | None = Field(default=None, pattern=r"^\d{5}$")
    area_ha: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=4)

    @model_validator(mode="after")
    def _dane_completo(self) -> "FincaCreate":
        if (self.departamento_dane is None) != (self.municipio_dane is None):
            raise ValueError("Envíe departamento y municipio juntos.")
        if self.departamento_dane and self.municipio_dane:
            if not codigos_dane_validos(self.departamento_dane, self.municipio_dane):
                raise ValueError("El municipio no corresponde al departamento.")
        return self


class FincaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombre: str
    departamento_dane: str | None = None
    municipio_dane: str | None = None
    area_ha: Decimal | None = None


class LoteCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    area: Decimal = Field(gt=0, max_digits=10, decimal_places=4)
    notas: str | None = Field(default=None, max_length=500)


class LoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    finca_id: UUID
    nombre: str
    area: Decimal
    notas: str | None = None
