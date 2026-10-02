from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FincaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    ubicacion: str | None = None


class FincaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombre: str


class LoteCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    area: Decimal = Field(gt=0, max_digits=10, decimal_places=4)


class LoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    finca_id: UUID
    nombre: str
    area: Decimal
