"""Configuración tipada leída del entorno o de un .env fuera de git."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AGRO_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AgroGestion API"
    api_prefix: str = "/api/v1"
    debug: bool = False

    # Sin valor por defecto: si falta un secreto, el arranque falla.
    secret_key: str
    database_url: str

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=60, ge=5, le=1440)
    politica_version: str = "2026-09"
    consultas_por_dia: int = Field(default=20, ge=1, le=500)
    noticias_dias_vigencia: int = Field(default=7, ge=1, le=60)
    log_level: str = "INFO"

    # Orígenes de navegador permitidos; una app móvil nativa no envía Origin.
    cors_origins: list[str] = [
        "http://localhost:8030",
        "http://127.0.0.1:8030",
        "http://localhost:3000",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
