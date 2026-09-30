import uuid
from datetime import date, datetime
from typing import Self

from pydantic import Field, model_validator

from app.core.catalogos import EstadoConocimiento, TipoManejo, TipoProblema
from app.schemas.common import Entrada, Salida


class FuenteCrear(Entrada):
    nombre: str = Field(min_length=1, max_length=120)
    url: str | None = Field(default=None, max_length=255)
    fecha: date | None = None
    licencia: str | None = Field(default=None, max_length=80)


class FuenteSalida(Salida):
    id: uuid.UUID
    nombre: str
    url: str | None
    fecha: date | None
    licencia: str | None


class SintomaEntrada(Entrada):
    descripcion: str = Field(min_length=3, max_length=1000)
    parte: str | None = Field(default=None, max_length=30)
    fase_o_edad: str | None = Field(default=None, max_length=30)


class ManejoEntrada(Entrada):
    tipo: TipoManejo
    descripcion: str = Field(min_length=3, max_length=2000)
    producto_ica: str | None = Field(default=None, max_length=120)
    fuente_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def _quimico_con_registro(self) -> Self:
        if self.tipo in ("quimico", "veterinario") and not self.producto_ica:
            raise ValueError("Un manejo químico o veterinario debe indicar el producto registrado.")
        return self


class ProblemaCrear(Entrada):
    nombre: str = Field(min_length=3, max_length=120)
    tipo: TipoProblema
    cultivo_id: uuid.UUID | None = None
    causa: str | None = Field(default=None, max_length=2000)
    sintomas: list[SintomaEntrada] = Field(default_factory=list, max_length=30)
    manejos: list[ManejoEntrada] = Field(default_factory=list, max_length=30)


class CambiarEstado(Entrada):
    estado: EstadoConocimiento
    observacion: str | None = Field(default=None, max_length=1000)


class SintomaSalida(Salida):
    descripcion: str
    parte: str | None
    fase_o_edad: str | None


class ManejoSalida(Salida):
    tipo: str
    descripcion: str
    producto_ica: str | None
    fuente: FuenteSalida | None


class ValidacionSalida(Salida):
    estado: str
    experto_id: uuid.UUID
    observacion: str | None
    creado_en: datetime


class ProblemaResumen(Salida):
    id: uuid.UUID
    nombre: str
    tipo: str
    cultivo_id: uuid.UUID | None
    estado: str


class ProblemaSalida(ProblemaResumen):
    causa: str | None
    sintomas: list[SintomaSalida]
    manejos: list[ManejoSalida]
    aviso: str = "Es una orientación basada en una ficha revisada; no reemplaza a un técnico."


class ProblemaRevision(ProblemaSalida):
    validaciones: list[ValidacionSalida]
