"""QR generation and lookup service for session result links."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import qrcode

from app.core.config import get_settings
from app.image.templates import PROJECT_ROOT, resolve_project_path
from app.models.session import SessionMetadata
from app.services.session_service import (
    InvalidSessionIdError,
    get_final_image_for_session,
    project_relative,
    read_session_metadata,
    save_session_metadata,
    session_dir,
    validate_session_id,
)


QR_FILENAME = "qr.png"


class SessionQrNotFoundError(FileNotFoundError):
    """Raised when a session exists but its QR image is missing."""


def build_result_image_url(session_id: str, public_base_url: str | None = None) -> str:
    """Build the URL encoded into the QR.

    Kept separate so Phase 5+ can switch this to a gallery URL without
    touching QR image generation.
    """

    safe_session_id = validate_session_id(session_id)
    base_url = (public_base_url or get_settings().public_base_url).rstrip("/") + "/"
    return urljoin(base_url, f"sessions/{safe_session_id}/image")


def qr_image_path(session_id: str) -> Path:
    return session_dir(session_id) / QR_FILENAME


def _assert_qr_path_is_safe(path: Path) -> None:
    output_root = (PROJECT_ROOT / "output" / "sessions").resolve()
    resolved = path.resolve()
    if output_root not in resolved.parents:
        raise InvalidSessionIdError("QR image path must stay below output/sessions.")


def generate_session_qr(session_id: str, target_url: str | None = None) -> SessionMetadata:
    """Generate or regenerate the session QR PNG and update metadata."""

    safe_session_id = validate_session_id(session_id)
    metadata = read_session_metadata(safe_session_id)
    get_final_image_for_session(safe_session_id)

    result_url = target_url or metadata.qr_target_url or build_result_image_url(safe_session_id)
    path = qr_image_path(safe_session_id)
    _assert_qr_path_is_safe(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    image = qrcode.make(result_url)
    image.save(path)

    updated = metadata.model_copy(
        update={
            "updated_at": datetime.now(timezone.utc),
            "qr_image_path": project_relative(path),
            "qr_target_url": result_url,
        }
    )
    return save_session_metadata(updated)


def get_qr_image_for_session(session_id: str) -> Path:
    """Return the stored QR image path for a session."""

    safe_session_id = validate_session_id(session_id)
    metadata = read_session_metadata(safe_session_id)

    if metadata.qr_image_path:
        path = resolve_project_path(metadata.qr_image_path).resolve()
    else:
        path = qr_image_path(safe_session_id)

    _assert_qr_path_is_safe(path)
    if not path.exists():
        raise SessionQrNotFoundError(f"QR image not found for session: {safe_session_id}")
    return path
