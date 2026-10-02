"""Respuestas y tipos compartidos por todos los esquemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer

from app.core.catalogos import EstadoIndicador

T = TypeVar("T")

# Los decimales se calculan exactos en el servidor y salen como número para el cliente móvil.
Decimal2 = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


def _a_dia(valor: object) -> object:
    return valor.date() if isinstance(valor, datetime) else valor


Dia = Annotated[date, BeforeValidator(_a_dia)]


class Entrada(BaseModel):
    """Base de los esquemas de entrada: rechaza campos no declarados."""

    model_config = ConfigDict(extra="forbid")


class Salida(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ReadyResponse(HealthResponse):
    base_de_datos: str


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    has_more: bool


class DetalleError(BaseModel):
    campo: str
    mensaje: str
    tipo: str


class ErrorDetalle(BaseModel):
    code: str
    message: str
    action: str | None = None
    details: list[DetalleError] | None = None


class ErrorRespuesta(BaseModel):
    """Formato único de error: decida siempre con `error.code`, nunca con `error.message`."""

    error: ErrorDetalle


class Indicador(BaseModel):
    titulo: str
    valor: float | None
    unidad: str
    explicacion: str
    estado: EstadoIndicador
    que_hacer: str | None = None
    fecha_datos: date | None = None
