"""Create sample inputs and run the Phase 2 demo composition."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from app.image.templates import resolve_project_path
from app.services.compose_service import compose_session


SAMPLE_IMAGES = {
    "assets/old-photos/old_1.jpg": ("OLD 1", "#6b4e3d", (900, 620)),
    "assets/old-photos/old_2.jpg": ("OLD 2", "#3d5f6b", (620, 900)),
    "captures/demo/current_1.jpg": ("CURRENT 1", "#7a2f46", (1400, 900)),
    "captures/demo/current_2.jpg": ("CURRENT 2", "#345c2e", (900, 1400)),
}


def create_sample_image(path: Path, label: str, color: str, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(image)

    margin = 40
    draw.rectangle(
        (margin, margin, size[0] - margin, size[1] - margin),
        outline="#ffffff",
        width=12,
    )
    draw.text((margin + 28, margin + 28), label, fill="#ffffff")
    draw.line((0, 0, size[0], size[1]), fill="#ffffff", width=8)
    draw.line((0, size[1], size[0], 0), fill="#ffffff", width=8)
    image.save(path, format="JPEG", quality=92)


def ensure_demo_samples(overwrite: bool = False) -> None:
    for relative_path, (label, color, size) in SAMPLE_IMAGES.items():
        path = resolve_project_path(relative_path)
        if path.exists() and not overwrite:
            continue
        create_sample_image(path, label, color, size)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 2 demo image composition.")
    parser.add_argument("--session-id", default="demo", help="Session id to compose.")
    parser.add_argument(
        "--create-samples",
        action="store_true",
        help="Create missing demo input images before composing.",
    )
    parser.add_argument(
        "--overwrite-samples",
        action="store_true",
        help="Regenerate demo input images even when they already exist.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.create_samples or args.overwrite_samples:
        ensure_demo_samples(overwrite=args.overwrite_samples)

    output_path = compose_session(session_id=args.session_id)
    print(output_path)


if __name__ == "__main__":
    main()
