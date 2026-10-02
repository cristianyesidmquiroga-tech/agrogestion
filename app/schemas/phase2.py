from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ActividadCreate(BaseModel):
    ciclo_id: UUID
    nombre: str = Field(min_length=2, max_length=150)
    fase: str = Field(min_length=2, max_length=80)
    fecha_inicio: datetime
    fecha_fin: datetime | None = None
    area_trabajada: Decimal = Field(gt=0, max_digits=10, decimal_places=4)


class CicloCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    fecha_inicio: datetime
    fecha_fin: datetime | None = None


class CicloResponse(ReadModel):
    id: UUID
    finca_id: UUID
    nombre: str
    estado: str
    fecha_inicio: datetime
    fecha_fin: datetime | None


class ActividadResponse(ReadModel):
    id: UUID
    finca_id: UUID
    ciclo_id: UUID
    nombre: str
    fase: str
    fecha_inicio: datetime
    fecha_fin: datetime | None
    area_trabajada: Decimal
    estado: str


class ActividadUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    fase: str | None = Field(default=None, min_length=2, max_length=80)
    fecha_fin: datetime | None = None
    area_trabajada: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=4)


class TrabajadorCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    tipo: str = Field(min_length=2, max_length=40)
    jornal_habitual: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    documento: str | None = None
    telefono: str | None = Field(default=None, max_length=30)


class TrabajadorResponse(ReadModel):
    id: UUID
    finca_id: UUID
    nombre: str
    tipo: str
    jornal_habitual: Decimal
    documento_ultimos4: str | None
    telefono: str | None
    estado: str


class TrabajadorUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    tipo: str | None = Field(default=None, min_length=2, max_length=40)
    jornal_habitual: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    documento: str | None = None
    telefono: str | None = Field(default=None, max_length=30)


class JornalCreate(BaseModel):
    trabajador_id: UUID | None = None
    actividad_id: UUID
    ciclo_id: UUID
    fecha: datetime
    obreros: Decimal = Field(gt=0, max_digits=6, decimal_places=2)
    dias: Decimal = Field(gt=0, max_digits=6, decimal_places=2)
    valor_jornal: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    modalidad: str = Field(default="jornal", pattern="^(jornal|destajo|por_kilo|contrato_global)$")


class JornalResponse(ReadModel):
    id: UUID
    finca_id: UUID
    trabajador_id: UUID | None
    actividad_id: UUID
    ciclo_id: UUID
    fecha: datetime
    obreros: Decimal
    dias: Decimal
    valor_jornal: Decimal
    modalidad: str
    total: Decimal
    estado: str


class InsumoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    unidad: str = Field(min_length=1, max_length=30)


class MovimientoCreate(BaseModel):
    insumo_id: UUID
    cantidad: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    fecha: datetime
    costo: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    actividad_id: UUID | None = None


class MovimientoResponse(ReadModel):
    id: UUID
    finca_id: UUID
    insumo_id: UUID
    actividad_id: UUID | None
    tipo: str
    cantidad: Decimal
    costo: Decimal
    fecha: datetime
    creado_por: UUID


class InsumoResponse(ReadModel):
    id: UUID
    finca_id: UUID
    nombre: str
    unidad: str
    existencia: Decimal
    estado: str


class CosechaCreate(BaseModel):
    ciclo_id: UUID
    cantidad: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    unidad: str = Field(min_length=1, max_length=30)
    calidad: str | None = None
    fecha: datetime


class CosechaResponse(ReadModel):
    id: UUID
    finca_id: UUID
    ciclo_id: UUID
    cantidad: Decimal
    unidad: str
    calidad: str | None
    fecha: datetime


class CosechaAcumuladoResponse(BaseModel):
    finca_id: UUID
    ciclo_id: UUID
    total: Decimal
    registros: list[CosechaResponse]


class ProcesoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    producto: str = Field(min_length=2, max_length=150)
    materia_prima: str = Field(min_length=2, max_length=150)
    origen_materia: str = Field(pattern="^(propia|comprada)$")
    fecha_inicio: datetime


class ProcesoResponse(ReadModel):
    id: UUID
    finca_id: UUID
    nombre: str
    producto: str
    materia_prima: str
    origen_materia: str
    fecha_inicio: datetime
    fecha_fin: datetime | None


class EtapaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    dias_estimados: Decimal = Field(gt=0, max_digits=6, decimal_places=2)


class EtapaResponse(ReadModel):
    id: UUID
    proceso_id: UUID
    finca_id: UUID
    nombre: str
    dias_estimados: Decimal
    iniciado_en: datetime | None
    finalizado_en: datetime | None


class GastoCreate(BaseModel):
    categoria: str = Field(min_length=2, max_length=80)
    monto: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    fecha: datetime
    ciclo_id: UUID | None = None


class IngresoCreate(BaseModel):
    categoria: str = Field(min_length=2, max_length=80)
    cantidad: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    precio_unitario: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    total: Decimal | None = None
    fecha: datetime
    ciclo_id: UUID | None = None
    comprador: str | None = None

    @model_validator(mode="after")
    def calculate_total(self) -> "IngresoCreate":
        expected = self.cantidad * self.precio_unitario
        if self.total is not None and self.total != expected:
            raise ValueError("El total no coincide con cantidad por precio unitario")
        self.total = expected
        return self


class ContableResponse(ReadModel):
    id: UUID
    finca_id: UUID
    categoria: str
    monto: Decimal | None = None
    total: Decimal | None = None
    estado: str


class EtapasMetricasResponse(BaseModel):
    proceso_id: UUID
    dias_estimados: Decimal
    dias_reales: Decimal
    diferencia: Decimal


class AnulacionCreate(BaseModel):
    motivo: str = Field(min_length=5, max_length=500)


class LineaVentaCreate(BaseModel):
    cosecha_id: UUID
    categoria: str = Field(min_length=2, max_length=80)
    unidad: str = Field(min_length=1, max_length=30)
    cantidad: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    merma: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    precio_unitario: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


class VentaCreate(BaseModel):
    comprador: str | None = None
    fecha: datetime
    lineas: list[LineaVentaCreate] = Field(min_length=1)


class VentaResponse(ReadModel):
    id: UUID
    finca_id: UUID
    comprador: str | None
    fecha: datetime
    estado: str
    total: Decimal


class PrecioCreate(BaseModel):
    categoria: str = Field(min_length=2, max_length=80)
    unidad: str = Field(min_length=1, max_length=30)
    precio: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    vigente_desde: datetime
    vigente_hasta: datetime | None = None


class PrecioResponse(ReadModel):
    id: UUID
    finca_id: UUID
    categoria: str
    unidad: str
    precio: Decimal
    vigente_desde: datetime
    vigente_hasta: datetime | None


class FlujoCajaResponse(BaseModel):
    finca_id: UUID
    ciclo_id: UUID | None = None
    anio: int
    mes: int
    ingresos: Decimal
    gastos: Decimal
    saldo: Decimal
