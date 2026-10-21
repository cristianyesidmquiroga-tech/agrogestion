import uuid
from datetime import datetime

from app.schemas.common import Decimal2, Salida


class UsuarioResumen(Salida):
    id: uuid.UUID
    email: str
    nombre: str
    rol: str
    activo: bool
    creado_en: datetime
    ultimo_acceso: datetime | None
    municipio_dane: str | None
    fincas: int
    siembras: int


class FincaDeUsuario(Salida):
    id: uuid.UUID
    nombre: str
    departamento_dane: str | None
    municipio_dane: str | None
    area_ha: Decimal2 | None
    siembras: int
    cosechas: int
    gastos: Decimal2
    ingresos: Decimal2


class UsuarioDetalle(UsuarioResumen):
    bloqueado: bool
    cosechas: int
    gastos: Decimal2
    ingresos: Decimal2
    detalle_fincas: list[FincaDeUsuario]
