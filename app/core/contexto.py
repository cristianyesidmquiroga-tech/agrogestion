"""Datos de quien hace la petición; lo usan los servicios sin depender de FastAPI."""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class UsuarioActual:
    id: uuid.UUID
    rol: str
