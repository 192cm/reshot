"""Camera integration service for capture requests."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.camera.dummy import capture_dummy
from app.core.config import get_settings
from app.image.templates import PROJECT_ROOT
from app.models.session import SessionMetadata
from app.services.session_service import (
    InvalidSessionIdError,
    SessionNotFoundError,
    read_session_metadata,
    save_session_metadata,
    validate_session_id,
)


class InvalidCaptureSlotError(ValueError):
    """Raised when the requested capture slot is unsupported."""


class UnsupportedCameraModeError(ValueError):
    """Raised when the configured camera mode is outside the current scope."""


MAX_CAPTURE_SLOTS = 8


def capture_path(session_id: str, slot: int) -> Path:
    safe_session_id = validate_session_id(session_id)
    if slot < 1 or slot > MAX_CAPTURE_SLOTS:
        raise InvalidCaptureSlotError(f"slot must be 1 to {MAX_CAPTURE_SLOTS}.")

    path = (PROJECT_ROOT / "captures" / safe_session_id / f"current_{slot}.jpg").resolve()
    captures_root = (PROJECT_ROOT / "captures").resolve()
    if captures_root not in path.parents:
        raise InvalidSessionIdError("capture path must stay below captures/.")
    return path


def capture_session_photo(session_id: str, slot: int) -> SessionMetadata:
    metadata = read_session_metadata(session_id, infer_from_final_image=False)
    destination = capture_path(metadata.session_id, slot)

    settings = get_settings()
    if settings.camera_mode != "dummy":
        raise UnsupportedCameraModeError(
            f"CAMERA_MODE={settings.camera_mode} is not implemented yet."
        )

    capture_dummy(slot, destination)

    captured_slots = [
        index
        for index in range(1, MAX_CAPTURE_SLOTS + 1)
        if capture_path(metadata.session_id, index).exists()
    ]
    status = "ready_to_select" if len(captured_slots) == MAX_CAPTURE_SLOTS else f"captured_{slot}"
    updated = metadata.model_copy(
        update={
            "status": status,
            "updated_at": datetime.now(timezone.utc),
            "captures": [
                f"captures/{metadata.session_id}/current_{index}.jpg"
                for index in captured_slots
            ],
        }
    )
    return save_session_metadata(updated)


def get_capture_image_for_session(session_id: str, slot: int) -> Path:
    try:
        read_session_metadata(session_id, infer_from_final_image=False)
    except SessionNotFoundError:
        raise

    path = capture_path(session_id, slot)
    if not path.exists():
        raise FileNotFoundError(f"Capture image not found: captures/{session_id}/current_{slot}.jpg")
    return path
