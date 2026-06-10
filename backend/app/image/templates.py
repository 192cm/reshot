"""Template loading helpers for frame JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.image.layout import FrameTemplate, template_from_dict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TEMPLATE_DIR = PROJECT_ROOT / "assets" / "frames"


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def load_template(template_id: str = "default", template_dir: Path | None = None) -> FrameTemplate:
    base_dir = template_dir or DEFAULT_TEMPLATE_DIR
    template_path = base_dir / f"{template_id}.json"
    if not template_path.exists():
        raise FileNotFoundError(f"Frame template not found: {template_path}")

    with template_path.open("r", encoding="utf-8") as file:
        raw: Any = json.load(file)

    if not isinstance(raw, dict):
        raise ValueError(f"Frame template must be a JSON object: {template_path}")

    template = template_from_dict(raw)
    if template.id != template_id:
        raise ValueError(
            f"Frame template id mismatch: expected '{template_id}', found '{template.id}'."
        )
    return template
