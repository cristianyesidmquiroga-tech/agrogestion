from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite+aiosqlite:///./agrogestion.db"
    jwt_secret: str = Field(min_length=16)
    field_encryption_key: str = ""
    allowed_origins: str = "http://localhost:3000"
    login_max_attempts: int = 5
    login_lock_minutes: int = 15
    jwt_expire_minutes: int = 60
    alert_allowed_hosts: str = ""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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
    return Settings()  # type: ignore[call-arg]
