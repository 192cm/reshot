"""File-backed session metadata storage."""

from __future__ import annotations

import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.image.templates import PROJECT_ROOT, resolve_project_path
from app.models.session import SessionMetadata
from app.services.compose_service import DEFAULT_OLD_PHOTOS, default_output_path, default_photo_paths


SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
SESSION_FILENAME = "session.json"


class InvalidSessionIdError(ValueError):
    """Raised when a session id is not safe for filesystem use."""


class SessionNotFoundError(FileNotFoundError):
    """Raised when session metadata cannot be found or inferred."""


class SessionImageNotFoundError(FileNotFoundError):
    """Raised when a session exists but its final image is missing."""


class SessionMetadataError(ValueError):
    """Raised when session metadata exists but cannot be parsed."""


def validate_session_id(session_id: str) -> str:
    if not SESSION_ID_PATTERN.fullmatch(session_id):
        raise InvalidSessionIdError(
            "session_id must use 1-64 letters, numbers, underscores, or hyphens."
        )
    return session_id


def project_relative(path: Path | str) -> str:
    resolved = resolve_project_path(path).resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(f"Path is outside the project root: {resolved}") from exc


def session_dir(session_id: str) -> Path:
    safe_session_id = validate_session_id(session_id)
    path = (PROJECT_ROOT / "output" / "sessions" / safe_session_id).resolve()
    output_root = (PROJECT_ROOT / "output" / "sessions").resolve()
    if path != output_root and output_root not in path.parents:
        raise InvalidSessionIdError("session directory must stay below output/sessions.")
    return path


def session_json_path(session_id: str) -> Path:
    return session_dir(session_id) / SESSION_FILENAME


def final_image_path(session_id: str) -> Path:
    return default_output_path(validate_session_id(session_id)).resolve()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def generate_session_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = secrets.token_hex(3)
    return f"{timestamp}-{suffix}"


def _default_captures(session_id: str) -> list[str]:
    paths = default_photo_paths(session_id)
    return [
        project_relative(paths["current_1"]),
        project_relative(paths["current_2"]),
    ]


def _default_old_photos() -> list[str]:
    return [
        project_relative(DEFAULT_OLD_PHOTOS["old_1"]),
        project_relative(DEFAULT_OLD_PHOTOS["old_2"]),
    ]


def build_session_metadata(
    session_id: str,
    *,
    status: str = "composed",
    template_id: str = "default",
    final_image: Path | str | None = None,
    old_photos: list[str] | None = None,
    captures: list[str] | None = None,
    existing: SessionMetadata | None = None,
) -> SessionMetadata:
    safe_session_id = validate_session_id(session_id)
    timestamp = _now()
    return SessionMetadata(
        session_id=safe_session_id,
        created_at=existing.created_at if existing else timestamp,
        updated_at=timestamp,
        status=status,
        template_id=template_id,
        final_image_path=project_relative(final_image or final_image_path(safe_session_id)),
        qr_image_path=existing.qr_image_path if existing else None,
        old_photos=old_photos or _default_old_photos(),
        captures=captures or _default_captures(safe_session_id),
    )


def save_session_metadata(metadata: SessionMetadata) -> SessionMetadata:
    safe_session_id = validate_session_id(metadata.session_id)
    path = session_json_path(safe_session_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(metadata.model_dump(mode="json"), file, ensure_ascii=False, indent=2)
        file.write("\n")

    return metadata


def write_session_metadata(
    session_id: str,
    *,
    status: str = "composed",
    template_id: str = "default",
    final_image: Path | str | None = None,
    old_photos: list[str] | None = None,
    captures: list[str] | None = None,
) -> SessionMetadata:
    existing = None
    try:
        existing = read_session_metadata(session_id, infer_from_final_image=False)
    except SessionNotFoundError:
        existing = None

    metadata = build_session_metadata(
        session_id,
        status=status,
        template_id=template_id,
        final_image=final_image,
        old_photos=old_photos,
        captures=captures,
        existing=existing,
    )
    return save_session_metadata(metadata)


def create_session(template_id: str = "default") -> SessionMetadata:
    """Create a file-backed session ready for Phase 5 capture."""

    session_id = generate_session_id()
    metadata = build_session_metadata(
        session_id,
        status="created",
        template_id=template_id,
    )
    session_dir(session_id).mkdir(parents=True, exist_ok=True)
    return save_session_metadata(metadata)


def update_session_status(session_id: str, status: str) -> SessionMetadata:
    metadata = read_session_metadata(session_id, infer_from_final_image=False)
    updated = metadata.model_copy(
        update={
            "updated_at": _now(),
            "status": status,
        }
    )
    return save_session_metadata(updated)


def read_session_metadata(
    session_id: str,
    *,
    infer_from_final_image: bool = True,
) -> SessionMetadata:
    safe_session_id = validate_session_id(session_id)
    path = session_json_path(safe_session_id)
    if not path.exists():
        if infer_from_final_image and final_image_path(safe_session_id).exists():
            return write_session_metadata(safe_session_id)
        raise SessionNotFoundError(f"Session not found: {safe_session_id}")

    try:
        with path.open("r", encoding="utf-8") as file:
            raw: Any = json.load(file)
        return SessionMetadata.model_validate(raw)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise SessionMetadataError(f"Invalid session metadata: {path}") from exc


def get_final_image_for_session(session_id: str) -> Path:
    metadata = read_session_metadata(session_id)
    image_path = resolve_project_path(metadata.final_image_path).resolve()
    output_root = (PROJECT_ROOT / "output" / "sessions").resolve()
    if output_root not in image_path.parents:
        raise InvalidSessionIdError("final image path must stay below output/sessions.")
    if not image_path.exists():
        raise SessionImageNotFoundError(f"Final image not found: {metadata.final_image_path}")
    return image_path
