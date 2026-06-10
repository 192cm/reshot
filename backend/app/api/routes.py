from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core.config import get_settings
from app.models.session import SessionMetadata
from app.services.camera_service import (
    InvalidCaptureSlotError,
    UnsupportedCameraModeError,
    capture_session_photo,
    get_capture_image_for_session,
)
from app.services.compose_service import compose_session
from app.services.qr_service import (
    SessionQrNotFoundError,
    generate_session_qr,
    get_qr_image_for_session,
)
from app.services.session_service import (
    InvalidSessionIdError,
    SessionImageNotFoundError,
    SessionMetadataError,
    SessionNotFoundError,
    get_final_image_for_session,
    create_session,
    read_session_metadata,
)
from app.image.templates import resolve_project_path

router = APIRouter()


class ComposeRequest(BaseModel):
    template_id: str = "default"


class CreateSessionRequest(BaseModel):
    template_id: str = "default"


class CaptureRequest(BaseModel):
    slot: int


def _session_error_to_http(exc: Exception) -> HTTPException:
    if isinstance(exc, (InvalidSessionIdError, InvalidCaptureSlotError)):
        return HTTPException(status_code=400, detail=str(exc))
    if isinstance(
        exc,
        (SessionNotFoundError, SessionImageNotFoundError, SessionQrNotFoundError, FileNotFoundError),
    ):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, SessionMetadataError):
        return HTTPException(status_code=500, detail=str(exc))
    if isinstance(exc, UnsupportedCameraModeError):
        return HTTPException(status_code=501, detail=str(exc))
    return HTTPException(status_code=500, detail="Unexpected session error.")


@router.get("/")
def read_root() -> dict[str, str]:
    settings = get_settings()
    return {"app": settings.app_name, "status": "ok"}


@router.get("/health")
def read_health() -> dict[str, object]:
    settings = get_settings()
    return {
        "app": settings.app_name,
        "status": "ok",
        "environment": settings.environment,
        "camera_mode": settings.camera_mode,
        "paths": {
            "captures": str(settings.captures_dir),
            "output": str(settings.output_dir),
            "assets": str(settings.assets_dir),
        },
    }


@router.get("/sessions/{session_id}", response_model=SessionMetadata)
def get_session(session_id: str) -> SessionMetadata:
    try:
        return read_session_metadata(session_id)
    except Exception as exc:
        raise _session_error_to_http(exc) from exc


@router.post("/sessions", response_model=SessionMetadata)
def create_session_endpoint(request: CreateSessionRequest | None = None) -> SessionMetadata:
    try:
        template_id = request.template_id if request else "default"
        return create_session(template_id=template_id)
    except Exception as exc:
        raise _session_error_to_http(exc) from exc


@router.post("/sessions/{session_id}/capture", response_model=SessionMetadata)
def capture_session_endpoint(session_id: str, request: CaptureRequest) -> SessionMetadata:
    try:
        return capture_session_photo(session_id=session_id, slot=request.slot)
    except Exception as exc:
        raise _session_error_to_http(exc) from exc


@router.get("/sessions/{session_id}/capture/{slot}")
def get_session_capture(session_id: str, slot: int) -> FileResponse:
    try:
        image_path = get_capture_image_for_session(session_id, slot)
    except Exception as exc:
        raise _session_error_to_http(exc) from exc

    return FileResponse(
        path=image_path,
        media_type="image/jpeg",
        filename=f"reshot-{session_id}-current-{slot}.jpg",
    )


@router.get("/old-photos/{slot}")
def get_old_photo(slot: int) -> FileResponse:
    if slot not in (1, 2):
        raise HTTPException(status_code=400, detail="slot must be 1 or 2.")

    path = resolve_project_path(f"assets/old-photos/old_{slot}.jpg").resolve()
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Old photo not found for slot {slot}.")

    return FileResponse(
        path=path,
        media_type="image/jpeg",
        filename=f"old_{slot}.jpg",
    )


@router.get("/sessions/{session_id}/image")
def get_session_image(session_id: str) -> FileResponse:
    try:
        image_path = get_final_image_for_session(session_id)
    except Exception as exc:
        raise _session_error_to_http(exc) from exc

    return FileResponse(
        path=image_path,
        media_type="image/jpeg",
        filename=f"reshot-{session_id}.jpg",
    )


@router.post("/sessions/{session_id}/qr", response_model=SessionMetadata)
def generate_session_qr_endpoint(session_id: str) -> SessionMetadata:
    try:
        return generate_session_qr(session_id)
    except Exception as exc:
        raise _session_error_to_http(exc) from exc


@router.get("/sessions/{session_id}/qr")
def get_session_qr(session_id: str) -> FileResponse:
    try:
        qr_path = get_qr_image_for_session(session_id)
    except Exception as exc:
        raise _session_error_to_http(exc) from exc

    return FileResponse(
        path=qr_path,
        media_type="image/png",
        filename=f"reshot-{session_id}-qr.png",
    )


@router.post("/sessions/{session_id}/compose", response_model=SessionMetadata)
def compose_session_endpoint(
    session_id: str,
    request: ComposeRequest | None = None,
) -> SessionMetadata:
    try:
        template_id = request.template_id if request else "default"
        compose_session(session_id=session_id, template_id=template_id)
        generate_session_qr(session_id)
        return read_session_metadata(session_id)
    except Exception as exc:
        raise _session_error_to_http(exc) from exc
