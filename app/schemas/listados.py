from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LecturaModelo(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class JornalDetalle(LecturaModelo):
    id: UUID
    trabajador_id: UUID | None
    trabajador_nombre: str | None
    actividad_id: UUID
    actividad_nombre: str
    ciclo_id: UUID
    fecha: datetime
    obreros: Decimal
    dias: Decimal
    valor_jornal: Decimal
    modalidad: str
    total: Decimal
    estado: str
    pagado_en: datetime | None


class InsumoDetalle(LecturaModelo):
    id: UUID
    nombre: str
    unidad: str
    existencia: Decimal
    costo_promedio: Decimal | None
    valor: Decimal
    ultimo_movimiento: datetime | None
    estado: str


class ProcesoDetalle(LecturaModelo):
    id: UUID
    nombre: str
    producto: str
    materia_prima: str
    origen_materia: str
    fecha_inicio: datetime
    fecha_fin: datetime | None
    etapas: int
    etapas_finalizadas: int
    estado: str
