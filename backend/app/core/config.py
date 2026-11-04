from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ReBuild API"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "rebuild_db"
    mongodb_supports_transactions: bool = False

    jwt_secret_key: str = "change_this_secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    password_reset_token_expire_hours: int = 24

    cors_origins: str = "http://localhost:5173"

    auth_rate_limit: str = "5/minute"

    @field_validator("jwt_secret_key")
    @classmethod
    def jwt_secret_must_change_in_prod(cls, v: str, info) -> str:
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
