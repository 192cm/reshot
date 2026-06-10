from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "reshot"
    environment: str = "development"
    public_base_url: str = "http://localhost:8000"
    frontend_origins: str = "http://localhost:5173"
    captures_dir: Path = Field(default=Path("captures"))
    output_dir: Path = Field(default=Path("output/sessions"))
    assets_dir: Path = Field(default=Path("assets"))
    camera_mode: str = "dummy"

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
