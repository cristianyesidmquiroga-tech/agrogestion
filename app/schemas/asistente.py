import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.core.catalogos import Coincidencia, ValorRetroalimentacion
from app.schemas.common import Entrada, Salida


class ConsultaCrear(Entrada):
    siembra_id: uuid.UUID
    texto: str = Field(min_length=5, max_length=1000)


class CausaProbable(BaseModel):
    problema_id: uuid.UUID
    problema: str
    coincidencia: Coincidencia
    por_que: str
    fuentes: list[str]


class TratamientoValidado(BaseModel):
    problema: str
    producto_ica: str
    descripcion: str
    fuente: str | None


class RespuestaAsistente(BaseModel):
    """Lo que el asistente entiende de la descripción y lo que hay validado para ese cultivo."""

    lo_que_entendi: str
    causas_probables: list[CausaProbable]
    que_hacer: list[str]
    tratamientos: list[TratamientoValidado]
    mensaje_tratamiento: str
    cuando_llamar_al_tecnico: str
    aviso: str
    hay_informacion: bool


class MensajeSalida(Salida):
    id: uuid.UUID
    rol: Literal["usuario", "asistente"]
    texto: str
    creado_en: datetime


class ConsultaSalida(Salida):
    id: uuid.UUID
    contexto: str
    contexto_id: uuid.UUID
    creado_en: datetime
    pregunta: str
    respuesta: RespuestaAsistente
    mensaje_respuesta_id: uuid.UUID
    valoracion: ValorRetroalimentacion | None = None


class ConsultaResumen(Salida):
    id: uuid.UUID
    contexto_id: uuid.UUID
    creado_en: datetime
    pregunta: str
    valoracion: ValorRetroalimentacion | None = None


class RetroalimentacionEntrada(Entrada):
    valor: ValorRetroalimentacion
    comentario: str | None = Field(default=None, max_length=1000)


class RetroalimentacionSalida(Salida):
    mensaje_id: uuid.UUID
    valor: str
    comentario: str | None


class CalidadSalida(BaseModel):
    consultas: int
    con_valoracion: int
    sirvieron: int
    no_sirvieron: int
    equivocadas: int
    porcentaje_que_sirvio: float | None
    aviso: str | None = None
