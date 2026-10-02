import uuid
from typing import Self

from pydantic import Field, model_validator

from app.core.catalogos import (
    BaseDosis,
    Fase,
    MetodoPropagacion,
    PagoCosecha,
    Susceptibilidad,
    TipoCiclo,
    TipoRenovacion,
    UnidadConteo,
)
from app.schemas.common import Decimal2, Entrada, Salida


class FaseEntrada(Entrada):
    fase: Fase
    orden: int = Field(ge=1, le=20)
    dias_estimados: int | None = Field(default=None, ge=0, le=3650)
    por_validar: bool = True


class MetodoEntrada(Entrada):
    metodo: MetodoPropagacion
    dias_germinacion: int | None = Field(default=None, ge=0, le=3650)
    dias_vivero: int | None = Field(default=None, ge=0, le=3650)
    por_validar: bool = True


class DosisEntrada(Entrada):
    insumo_tipo: str = Field(min_length=1, max_length=30)
    dosis: Decimal2 = Field(gt=0, max_digits=10, decimal_places=3)
    unidad: str = Field(min_length=1, max_length=12)
    base: BaseDosis
    por_validar: bool = True


class CultivoBase(Entrada):
    nombre: str = Field(min_length=1, max_length=80)
    nombre_cientifico: str | None = Field(default=None, max_length=120)
    grupo: str = Field(min_length=1, max_length=30)
    tipo_ciclo: TipoCiclo
    unidad_conteo: UnidadConteo
    tipo_renovacion: TipoRenovacion | None = None
    unidad_cosecha: str = Field(min_length=1, max_length=12)
    pago_cosecha_sugerido: PagoCosecha | None = None
    densidad_ref: int | None = Field(default=None, ge=1)
    meses_primera_cosecha: int | None = Field(default=None, ge=0, le=600)
    cosechas_por_anio: Decimal2 | None = Field(
        default=None, ge=0, le=12, max_digits=3, decimal_places=1
    )
    por_validar: bool = True
    fuente: str | None = Field(default=None, max_length=200)
    fases: list[FaseEntrada] = Field(default_factory=list)
    metodos: list[MetodoEntrada] = Field(default_factory=list)
    dosis: list[DosisEntrada] = Field(default_factory=list)

    @model_validator(mode="after")
    def _coherente(self) -> Self:
        if self.tipo_ciclo == "transitorio" and self.tipo_renovacion is not None:
            raise ValueError("Un cultivo transitorio no tiene renovación.")
        if len({f.fase for f in self.fases}) != len(self.fases):
            raise ValueError("Una fase no puede repetirse.")
        if len({m.metodo for m in self.metodos}) != len(self.metodos):
            raise ValueError("Un método de propagación no puede repetirse.")
        return self


class CultivoCrear(CultivoBase):
    copiar_de: uuid.UUID | None = None


class CultivoActualizar(CultivoBase):
    pass


class FaseSalida(Salida):
    fase: str
    orden: int
    dias_estimados: int | None
    por_validar: bool


class MetodoSalida(Salida):
    metodo: str
    dias_germinacion: int | None
    dias_vivero: int | None
    por_validar: bool


class DosisSalida(Salida):
    insumo_tipo: str
    dosis: Decimal2
    unidad: str
    base: str
    por_validar: bool


class CultivoResumen(Salida):
    id: uuid.UUID
    nombre: str
    grupo: str
    tipo_ciclo: str
    unidad_conteo: str
    por_validar: bool


class CultivoSalida(CultivoResumen):
    nombre_cientifico: str | None
    tipo_renovacion: str | None
    unidad_cosecha: str
    pago_cosecha_sugerido: str | None
    densidad_ref: int | None
    meses_primera_cosecha: int | None
    cosechas_por_anio: Decimal2 | None
    fuente: str | None
    fases: list[FaseSalida]
    metodos: list[MetodoSalida]
    dosis: list[DosisSalida]


class RiesgoCrear(Entrada):
    nombre: str = Field(min_length=1, max_length=60)
    tipo: str = Field(pattern="^(clima|plaga|enfermedad|otro)$")
    aplica_a: str = Field(pattern="^(cultivo|animal|ambos)$")


class RiesgoSalida(Salida):
    id: uuid.UUID
    nombre: str
    tipo: str
    aplica_a: str


class CultivoRiesgoEntrada(Entrada):
    riesgo_id: uuid.UUID
    fase_critica: Fase | None = None
    susceptibilidad: Susceptibilidad
    medidas: str | None = Field(default=None, max_length=2000)
    por_validar: bool = True


class CultivoRiesgoSalida(Salida):
    riesgo_id: uuid.UUID
    fase_critica: str | None
    susceptibilidad: str
    medidas: str | None
    por_validar: bool
