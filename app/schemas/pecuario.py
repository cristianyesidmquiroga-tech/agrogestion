from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class EspecieCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    descripcion: str | None = None


class EspecieResponse(ReadModel):
    id: UUID
    finca_id: UUID
    nombre: str
    descripcion: str | None


class LoteAnimalCreate(BaseModel):
    especie_id: UUID
    nombre: str = Field(min_length=2, max_length=100)
    cantidad: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    ubicacion: str | None = None


class LoteAnimalResponse(ReadModel):
    id: UUID
    finca_id: UUID
    especie_id: UUID
    nombre: str
    cantidad: Decimal
    ubicacion: str | None


class AnimalCreate(BaseModel):
    especie_id: UUID
    lote_animal_id: UUID | None = None
    arete: str = Field(min_length=1, max_length=80)
    nombre: str | None = None
    sexo: str = Field(pattern="^(macho|hembra|indeterminado)$")
    raza: str | None = None
    nacimiento: datetime | None = None
    madre_id: UUID | None = None
    padre_id: UUID | None = None


class AnimalResponse(ReadModel):
    id: UUID
    finca_id: UUID
    especie_id: UUID
    lote_animal_id: UUID | None
    arete: str
    nombre: str | None
    sexo: str
    raza: str | None
    nacimiento: datetime | None
    madre_id: UUID | None
    padre_id: UUID | None
    estado: str


EVENT_TYPES = "^(vacunacion|tratamiento|pesaje|monta|prenez|parto|traslado|venta|muerte)$"


class EventoCreate(BaseModel):
    animal_id: UUID | None = None
    lote_animal_id: UUID | None = None
    tipo: str = Field(pattern=EVENT_TYPES)
    fecha: datetime
    producto: str | None = None
    dosis: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    retiro_hasta: datetime | None = None
    notas: str | None = None

    @model_validator(mode="after")
    def exactly_one_target(self) -> "EventoCreate":
        if (self.animal_id is None) == (self.lote_animal_id is None):
            raise ValueError("El evento debe apuntar a un animal o a un lote")
        return self


class EventoResponse(ReadModel):
    id: UUID
    finca_id: UUID
    animal_id: UUID | None
    lote_animal_id: UUID | None
    tipo: str
    fecha: datetime
    producto: str | None
    dosis: Decimal | None
    retiro_hasta: datetime | None
    notas: str | None


class ProduccionCreate(BaseModel):
    lote_animal_id: UUID
    fecha: datetime
    tipo: str = Field(min_length=2, max_length=30)
    cantidad: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    unidad: str = Field(min_length=1, max_length=30)


class ProduccionResponse(ReadModel):
    id: UUID
    finca_id: UUID
    lote_animal_id: UUID
    fecha: datetime
    tipo: str
    cantidad: Decimal
    unidad: str


class AlimentacionCreate(BaseModel):
    lote_animal_id: UUID
    alimento: str = Field(min_length=2, max_length=120)
    cantidad: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    costo: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    fecha: datetime


class AlimentacionResponse(ReadModel):
    id: UUID
    finca_id: UUID
    lote_animal_id: UUID
    alimento: str
    cantidad: Decimal
    costo: Decimal
    fecha: datetime


class AlertaResponse(ReadModel):
    id: UUID
    finca_id: UUID
    fuente_id: UUID
    tipo: str
    region_dane: str
    titulo: str
    resumen: str
    vigente_desde: datetime
    vigente_hasta: datetime

    @property
    def vigencia_texto(self) -> str:
        return f"Vigente desde {self.vigente_desde:%Y-%m-%d} hasta {self.vigente_hasta:%Y-%m-%d}"


class FuenteCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    url: str = Field(min_length=8, max_length=500)


class AlertaCreate(BaseModel):
    fuente_id: UUID
    tipo: str = Field(pattern="^(clima|sanidad)$")
    region_dane: str = Field(min_length=2, max_length=20)
    titulo: str = Field(min_length=2, max_length=200)
    resumen: str = Field(min_length=2)
    vigente_desde: datetime
    vigente_hasta: datetime

    @model_validator(mode="after")
    def valid_period(self) -> "AlertaCreate":
        if self.vigente_hasta <= self.vigente_desde:
            raise ValueError("La vigencia de la alerta no es válida")
        return self
