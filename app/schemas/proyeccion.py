import uuid
from decimal import Decimal

from pydantic import Field

from app.schemas.common import Entrada, Salida


class ProyeccionAgricolaEntrada(Entrada):
    cultivo_id: uuid.UUID
    area_m2: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class ProyeccionAgricolaSalida(Salida):
    area_m2: Decimal
    cultivo_nombre: str
    plantas_estimadas: int
    meses_primera_cosecha: int | None
    cosechas_por_anio: Decimal | None
    costo_semilla_estimado: Decimal
    costo_abono_estimado: Decimal
    ingreso_estimado_anual: Decimal
    utilidad_estimada_anual: Decimal
