"""Dummy camera adapter used before Nikon integration exists."""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw

from app.image.templates import resolve_project_path


DUMMY_SOURCES = {
    1: [
        "assets/dummy-captures/sample_1.jpg",
        "captures/demo/current_1.jpg",
        "assets/old-photos/old_1.jpg",
    ],
    2: [
        "assets/dummy-captures/sample_2.jpg",
        "captures/demo/current_2.jpg",
        "assets/old-photos/old_2.jpg",
    ],
}


def _create_fallback_image(path: Path, slot: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    palette = {1: "#305f72", 2: "#7a3f46"}
    size = (1400, 1000) if slot == 1 else (1000, 1400)
    image = Image.new("RGB", size, palette[slot])
    draw = ImageDraw.Draw(image)
    margin = 48
    draw.rectangle(
        (margin, margin, size[0] - margin, size[1] - margin),
        outline="#ffffff",
        width=14,
    )
    draw.text((margin + 32, margin + 32), f"DUMMY CAPTURE {slot}", fill="#ffffff")
    draw.line((0, 0, size[0], size[1]), fill="#ffffff", width=8)
    draw.line((0, size[1], size[0], 0), fill="#ffffff", width=8)
    image.save(path, format="JPEG", quality=92)


def capture_dummy(slot: int, destination: Path) -> Path:
    if slot not in (1, 2):
        raise ValueError("slot must be 1 or 2.")

    destination.parent.mkdir(parents=True, exist_ok=True)
    for relative_source in DUMMY_SOURCES[slot]:
        source = resolve_project_path(relative_source)
        if source.exists():
            shutil.copyfile(source, destination)
            return destination

    _create_fallback_image(destination, slot)
    return destination
