import uuid
from datetime import date

from pydantic import Field

from app.core.catalogos import MetodoPropagacion
from app.schemas.common import Entrada, Salida


class PropagacionCrear(Entrada):
    finca_id: uuid.UUID
    cultivo_id: uuid.UUID
    metodo: MetodoPropagacion
    fecha_inicio: date
    puestas: int = Field(ge=1)


class PropagacionActualizar(Entrada):
    germinadas: int | None = Field(default=None, ge=0)
    listas: int | None = Field(default=None, ge=0)
    perdidas: int | None = Field(default=None, ge=0)


class TrasplanteEntrada(Entrada):
    siembra_id: uuid.UUID
    cantidad: int = Field(ge=1)


class PropagacionSalida(Salida):
    id: uuid.UUID
    finca_id: uuid.UUID
    cultivo_id: uuid.UUID
    siembra_id: uuid.UUID | None
    metodo: str
    fecha_inicio: date
    puestas: int
    germinadas: int
    listas: int
    perdidas: int
    trasplantadas: int
