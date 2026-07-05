"""Google Drive upload service for composed session images."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, NamedTuple

from app.core.config import Settings, get_settings
from app.image.templates import resolve_project_path
from app.models.session import SessionMetadata
from app.services.session_service import (
    get_final_image_for_session,
    read_session_metadata,
    save_session_metadata,
    validate_session_id,
)


class GoogleDriveConfigurationError(RuntimeError):
    """Raised when Google Drive upload is enabled but not ready to run."""


class GoogleDriveUploadError(RuntimeError):
    """Raised when Google Drive rejects or fails an upload."""


class GoogleDriveLibraries(NamedTuple):
    Request: Any
    Credentials: Any
    InstalledAppFlow: Any
    build: Any
    HttpError: Any
    MediaFileUpload: Any


def _import_google_libraries() -> GoogleDriveLibraries:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        raise GoogleDriveConfigurationError(
            "Google Drive support is enabled, but the Google API packages are not installed. "
            "Run `pip install -r backend/requirements.txt`."
        ) from exc

    return GoogleDriveLibraries(
        Request=Request,
        Credentials=Credentials,
        InstalledAppFlow=InstalledAppFlow,
        build=build,
        HttpError=HttpError,
        MediaFileUpload=MediaFileUpload,
    )


def _configured_scopes(settings: Settings) -> list[str]:
    scopes = [scope.strip() for scope in settings.google_drive_scopes.split(",") if scope.strip()]
    if not scopes:
        raise GoogleDriveConfigurationError("GOOGLE_DRIVE_SCOPES must include at least one scope.")
    return scopes


def _resolve_config_path(path: Path) -> Path:
    return resolve_project_path(path).resolve()


def _save_credentials(credentials: Any, token_path: Path) -> None:
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(credentials.to_json(), encoding="utf-8")


def _token_file_has_scopes(token_path: Path, scopes: list[str]) -> bool:
    try:
        raw = json.loads(token_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    token_scopes = raw.get("scopes")
    if isinstance(token_scopes, str):
        granted = set(token_scopes.split())
    elif isinstance(token_scopes, list):
        granted = {scope for scope in token_scopes if isinstance(scope, str)}
    else:
        return True
    return set(scopes).issubset(granted)


def _load_authorized_credentials(
    settings: Settings,
    libraries: GoogleDriveLibraries,
    *,
    allow_interactive: bool,
) -> Any:
    scopes = _configured_scopes(settings)
    credentials_path = _resolve_config_path(settings.google_drive_credentials_file)
    token_path = _resolve_config_path(settings.google_drive_token_file)

    if not credentials_path.exists():
        raise GoogleDriveConfigurationError(
            f"Google Drive credentials file was not found: {credentials_path}"
        )

    credentials = None
    if token_path.exists():
        if not _token_file_has_scopes(token_path, scopes):
            if not allow_interactive:
                raise GoogleDriveConfigurationError(
                    "Google Drive token scopes do not match GOOGLE_DRIVE_SCOPES. "
                    "Run `python -m app.scripts.google_drive_auth` from the backend folder again."
                )
        else:
            credentials = libraries.Credentials.from_authorized_user_file(str(token_path), scopes)

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(libraries.Request())
        except Exception as exc:
            if not allow_interactive:
                raise GoogleDriveConfigurationError(
                    "Google Drive token could not be refreshed. "
                    "Run `python -m app.scripts.google_drive_auth` from the backend folder again."
                ) from exc
            credentials = None
        else:
            _save_credentials(credentials, token_path)
            return credentials

    if allow_interactive:
        flow = libraries.InstalledAppFlow.from_client_secrets_file(str(credentials_path), scopes)
        credentials = flow.run_local_server(port=0)
        _save_credentials(credentials, token_path)
        return credentials

    raise GoogleDriveConfigurationError(
        "Google Drive OAuth token is missing. "
        "Run `python -m app.scripts.google_drive_auth` from the backend folder once."
    )


def _build_drive_client(
    settings: Settings,
    libraries: GoogleDriveLibraries | None = None,
) -> tuple[Any, GoogleDriveLibraries]:
    libraries = libraries or _import_google_libraries()
    credentials = _load_authorized_credentials(
        settings,
        libraries,
        allow_interactive=False,
    )
    service = libraries.build("drive", "v3", credentials=credentials, cache_discovery=False)
    return service, libraries


def _drive_file_fields() -> str:
    return "id,webViewLink,webContentLink"


def _media_upload(libraries: GoogleDriveLibraries, image_path: Path) -> Any:
    return libraries.MediaFileUpload(str(image_path), mimetype="image/jpeg", resumable=False)


def _http_status(exc: Exception) -> int | None:
    response = getattr(exc, "resp", None)
    return getattr(response, "status", None)


def _format_http_error(prefix: str, exc: Exception) -> str:
    status = _http_status(exc)
    reason = getattr(getattr(exc, "resp", None), "reason", None)
    parts = [prefix]
    if status:
        parts.append(f"status {status}")
    if reason:
        parts.append(str(reason))
    message = ": ".join(parts)
    if status in (403, 404):
        message += " Check GOOGLE_DRIVE_FOLDER_ID and the OAuth account permissions."
    return message


def _create_drive_file(
    service: Any,
    libraries: GoogleDriveLibraries,
    *,
    image_path: Path,
    folder_id: str,
    filename: str,
) -> dict[str, Any]:
    body = {"name": filename, "parents": [folder_id]}
    return (
        service.files()
        .create(body=body, media_body=_media_upload(libraries, image_path), fields=_drive_file_fields())
        .execute()
    )


def _update_drive_file(
    service: Any,
    libraries: GoogleDriveLibraries,
    *,
    file_id: str,
    image_path: Path,
    filename: str,
) -> dict[str, Any] | None:
    try:
        return (
            service.files()
            .update(
                fileId=file_id,
                body={"name": filename},
                media_body=_media_upload(libraries, image_path),
                fields=_drive_file_fields(),
            )
            .execute()
        )
    except libraries.HttpError as exc:
        if _http_status(exc) in (403, 404):
            return None
        raise


def _ensure_public_reader(service: Any, libraries: GoogleDriveLibraries, file_id: str) -> None:
    try:
        (
            service.permissions()
            .create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"},
                fields="id",
            )
            .execute()
        )
    except libraries.HttpError as exc:
        if _http_status(exc) != 409:
            raise


def _get_drive_file(service: Any, file_id: str) -> dict[str, Any]:
    return service.files().get(fileId=file_id, fields=_drive_file_fields()).execute()


def _fallback_share_url(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"


def run_interactive_authorization() -> Path:
    """Create or refresh the local OAuth token used by the backend."""

    settings = get_settings()
    libraries = _import_google_libraries()
    _load_authorized_credentials(settings, libraries, allow_interactive=True)
    return _resolve_config_path(settings.google_drive_token_file)


def upload_final_image_to_drive(session_id: str) -> SessionMetadata:
    """Upload a session final image to the configured Google Drive folder."""

    safe_session_id = validate_session_id(session_id)
    settings = get_settings()
    metadata = read_session_metadata(safe_session_id)

    if not settings.google_drive_enabled:
        return metadata
    if not settings.google_drive_folder_id:
        raise GoogleDriveConfigurationError(
            "GOOGLE_DRIVE_FOLDER_ID is required when GOOGLE_DRIVE_ENABLED=true."
        )

    image_path = get_final_image_for_session(safe_session_id)
    filename = f"reshot-{safe_session_id}.jpg"

    libraries = _import_google_libraries()
    try:
        service, libraries = _build_drive_client(settings, libraries)
        drive_file = None
        if metadata.drive_file_id:
            drive_file = _update_drive_file(
                service,
                libraries,
                file_id=metadata.drive_file_id,
                image_path=image_path,
                filename=filename,
            )
        if drive_file is None:
            drive_file = _create_drive_file(
                service,
                libraries,
                image_path=image_path,
                folder_id=settings.google_drive_folder_id,
                filename=filename,
            )

        file_id = drive_file.get("id")
        if not file_id:
            raise GoogleDriveUploadError("Google Drive upload completed without a file id.")

        if settings.google_drive_share_public:
            _ensure_public_reader(service, libraries, file_id)

        drive_file = _get_drive_file(service, file_id)
    except GoogleDriveConfigurationError:
        raise
    except GoogleDriveUploadError:
        raise
    except libraries.HttpError as exc:
        raise GoogleDriveUploadError(_format_http_error("Google Drive upload failed", exc)) from exc
    except Exception as exc:
        raise GoogleDriveUploadError(f"Google Drive upload failed: {exc}") from exc

    file_id = drive_file["id"]
    share_url = drive_file.get("webViewLink") or _fallback_share_url(file_id)
    updated = metadata.model_copy(
        update={
            "updated_at": datetime.now(timezone.utc),
            "drive_file_id": file_id,
            "drive_share_url": share_url,
            "qr_target_url": share_url,
        }
    )
    return save_session_metadata(updated)