import uuid
from datetime import date
from typing import Self

from pydantic import Field, model_validator

from app.core.catalogos import MetodoPropagacion, TipoCicloSiembra
from app.schemas.common import Decimal2, Entrada, Indicador, Salida


class SiembraCrear(Entrada):
    finca_id: uuid.UUID
    lote_id: uuid.UUID
    cultivo_id: uuid.UUID
    metodo: MetodoPropagacion
    area_ha: Decimal2 = Field(gt=0, max_digits=10, decimal_places=4)
    plantas_sembradas: int | None = Field(default=None, ge=1)
    fecha_plan: date
    presupuesto: Decimal2 | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)


class CicloSalida(Salida):
    id: uuid.UUID
    tipo: str
    numero: int
    estado: str
    fecha_inicio: date | None
    fecha_fin: date | None
    motivo_perdida: str | None


class SiembraResumen(Salida):
    id: uuid.UUID
    finca_id: uuid.UUID
    lote_id: uuid.UUID
    cultivo_id: uuid.UUID
    metodo: str
    area_ha: Decimal2
    plantas_sembradas: int | None
    fecha_plan: date
    estado: str


class SiembraSalida(SiembraResumen):
    presupuesto: Decimal2 | None
    ciclos: list[CicloSalida]


class IniciarEntrada(Entrada):
    fecha_inicio: date | None = None


class CerrarCicloEntrada(Entrada):
    motivo_perdida: str | None = Field(default=None, min_length=3, max_length=500)
    fecha_fin: date | None = None


class CicloCrear(Entrada):
    tipo: TipoCicloSiembra


class ConteoCrear(Entrada):
    fecha: date
    vivas: int = Field(ge=0)
    muertas: int = Field(default=0, ge=0)
    resiembras: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def _fecha_valida(self) -> Self:
        if self.fecha > date.today():
            raise ValueError("La fecha del conteo no puede ser futura.")
        return self


class ConteoSalida(Salida):
    id: uuid.UUID
    fecha: date
    vivas: int
    muertas: int
    resiembras: int


class IndicesSalida(Salida):
    siembra_id: uuid.UUID
    fecha_conteo: date | None
    indicadores: list[Indicador]
    aviso: str | None = None


class FaseCronograma(Salida):
    fase: str
    orden: int
    dias_estimados: int | None
    por_validar: bool
    inicio_plan: date | None
    fin_plan: date | None
    inicio_real: date | None = None
    fin_real: date | None = None
    dias_retraso: int | None = None


class CronogramaSalida(Salida):
    ciclo_id: uuid.UUID
    tipo: str
    fecha_inicio: date | None
    fases: list[FaseCronograma]
    aviso: str | None = None


class NecesidadItem(Salida):
    insumo_tipo: str
    dosis: Decimal2
    unidad: str
    base: str
    cantidad_necesaria: float | None
    por_validar: bool
    mensaje: str | None = None


class NecesidadSalida(Salida):
    ciclo_id: uuid.UUID
    items: list[NecesidadItem]
    aviso: str | None = None
