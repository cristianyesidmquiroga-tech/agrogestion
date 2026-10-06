from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "AgroGestion API"
    database_url: str = "sqlite+aiosqlite:///./agrogestion.db"
    jwt_secret: str = Field(min_length=16)
    field_encryption_key: str = ""
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    login_max_attempts: int = 5
    login_lock_minutes: int = 15
    jwt_expire_minutes: int = Field(default=60, ge=5, le=1440)
    rate_limit: int | None = None
    alert_allowed_hosts: str = ""
    bcrypt_cost: int = Field(default=12, ge=4, le=15)
    politica_version: str = "2026-09"
    consultas_por_dia: int = Field(default=20, ge=1, le=500)
    noticias_dias_vigencia: int = Field(default=7, ge=1, le=60)
    log_level: str = "INFO"
    seed_password: str | None = None
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_ignore_empty=True, extra="ignore"
    )

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def allowed_alert_hosts(self) -> set[str]:
        return {
            host.strip().lower() for host in self.alert_allowed_hosts.split(",") if host.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
