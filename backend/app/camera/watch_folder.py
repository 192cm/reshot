"""Watch-folder camera adapter for tethered camera workflows."""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg"}


class WatchFolderTimeoutError(TimeoutError):
    """Raised when no usable capture appears before the timeout."""


def _snapshot_images(watch_dir: Path) -> set[Path]:
    return {
        path.resolve()
        for path in watch_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    }


def _is_file_stable(path: Path, stable_seconds: float = 0.5) -> bool:
    try:
        first_size = path.stat().st_size
        first_mtime = path.stat().st_mtime
        if first_size <= 0:
            return False
        time.sleep(stable_seconds)
        second_stat = path.stat()
    except OSError:
        return False

    return second_stat.st_size == first_size and second_stat.st_mtime == first_mtime


def _newest_candidate(watch_dir: Path, baseline: set[Path], started_at: float) -> Path | None:
    candidates: list[Path] = []
    for path in watch_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        resolved = path.resolve()
        try:
            modified_at = path.stat().st_mtime
        except OSError:
            continue

        if resolved not in baseline or modified_at >= started_at - 2:
            candidates.append(path)

    if not candidates:
        return None

    return max(candidates, key=lambda image_path: image_path.stat().st_mtime)


def _run_trigger_command(command: str, timeout_seconds: int, cwd: Path) -> None:
    try:
        subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f"Camera trigger command timed out after {timeout_seconds} seconds."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Camera trigger command failed with exit code {exc.returncode}.") from exc


def capture_from_watch_folder(
    watch_dir: Path,
    destination: Path,
    timeout_seconds: int,
    poll_interval_seconds: float = 0.25,
    trigger_command: str | None = None,
    trigger_timeout_seconds: int = 5,
) -> Path:
    watch_dir = watch_dir.expanduser().resolve()
    if not watch_dir.exists() or not watch_dir.is_dir():
        raise FileNotFoundError(f"Camera watch folder does not exist: {watch_dir}")

    started_at = time.time()
    baseline = _snapshot_images(watch_dir)

    if trigger_command:
        _run_trigger_command(trigger_command, trigger_timeout_seconds, watch_dir)

    deadline = started_at + timeout_seconds

    while time.time() < deadline:
        candidate = _newest_candidate(watch_dir, baseline, started_at)
        if candidate and _is_file_stable(candidate):
            destination.parent.mkdir(parents=True, exist_ok=True)
            if candidate.resolve() != destination.resolve():
                shutil.copy2(candidate, destination)
            return destination

        time.sleep(poll_interval_seconds)

    raise WatchFolderTimeoutError(
        f"No new JPG appeared in {watch_dir} within {timeout_seconds} seconds."
    )