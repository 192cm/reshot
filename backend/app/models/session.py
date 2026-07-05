"""Session domain models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SessionMetadata(BaseModel):
    session_id: str
    created_at: datetime
    updated_at: datetime
    status: str = "created"
    template_id: str = "default"
    final_image_path: str
    qr_image_path: str | None = None
    qr_target_url: str | None = None
    drive_file_id: str | None = None
    drive_share_url: str | None = None
    old_photos: list[str] = Field(default_factory=list)
    captures: list[str] = Field(default_factory=list)
