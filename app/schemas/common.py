"""Respuestas y tipos compartidos por todos los esquemas."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, PlainSerializer

from app.core.catalogos import EstadoIndicador

T = TypeVar("T")

# Los decimales se calculan exactos en el servidor y salen como número para el cliente móvil.
Decimal2 = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


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


class ErrorRespuesta(BaseModel):
    """Formato único de error: decida siempre con `error`, nunca con `message`."""

    error: str
    message: str
    status_code: int
    details: list[DetalleError] | None = None


class Indicador(BaseModel):
    titulo: str
    valor: float | None
    unidad: str
    explicacion: str
    estado: EstadoIndicador
    que_hacer: str | None = None
    fecha_datos: date | None = None
