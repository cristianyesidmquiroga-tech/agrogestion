import uuid

from pydantic import BaseModel

from app.core.catalogos import RolUsuario


class TokenSalida(BaseModel):
    """Respuesta del inicio de sesión. Envíe `access_token` como `Authorization: Bearer <token>`."""

    access_token: str
    token_type: str
    expires_in: int
    rol: RolUsuario
    nombre: str


class PermisoSalida(BaseModel):
    grupo: str
    metodo: str
    ruta: str
    resumen: str


class PerfilSalida(BaseModel):
    id: uuid.UUID
    nombre: str
    correo: str
    rol: RolUsuario
    fincas: list[uuid.UUID]
    permisos: list[PermisoSalida]
