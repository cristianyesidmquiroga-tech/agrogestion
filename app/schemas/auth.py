from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

COMMON_PASSWORDS = {"password123", "1234567890", "qwertyuiop", "agrogestion", "contraseña123"}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UsuarioCreate(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=10)
    rol: str = Field(default="agricultor", pattern="^(admin|agricultor|contador|experto)$")

    @field_validator("password")
    @classmethod
    def reject_common_password(cls, value: str) -> str:
        if value.lower() in COMMON_PASSWORDS:
            raise ValueError("La contraseña es demasiado común")
        return value


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    nombre: str
    rol: str
    activo: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    rol: str
    nombre: str


class PermisoResponse(BaseModel):
    grupo: str
    metodo: str
    ruta: str
    resumen: str


class PerfilResponse(UsuarioResponse):
    fincas: list[UUID]
    permisos: list[PermisoResponse]
