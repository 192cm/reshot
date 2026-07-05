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
    camera_watch_dir: Path | None = None
    camera_capture_timeout_seconds: int = 20
    camera_trigger_command: str | None = None
    camera_trigger_timeout_seconds: int = 5
    google_drive_enabled: bool = False
    google_drive_folder_id: str | None = None
    google_drive_credentials_file: Path = Field(default=Path("secrets/google/credentials.json"))
    google_drive_token_file: Path = Field(default=Path("secrets/google/token.json"))
    google_drive_share_public: bool = True
    google_drive_scopes: str = "https://www.googleapis.com/auth/drive"

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
