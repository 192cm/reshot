"""Image composition service for the 4-photo output."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.image.crop import center_crop_to_size, load_image
from app.image.layout import ImageBox, TextSpec
from app.image.templates import PROJECT_ROOT, load_template, resolve_project_path


DEFAULT_OLD_PHOTOS = {
    "old_1": "assets/old-photos/old_1.jpg",
    "old_2": "assets/old-photos/old_2.jpg",
}


def default_photo_paths(session_id: str) -> dict[str, Path]:
    return {
        "old_1": resolve_project_path(DEFAULT_OLD_PHOTOS["old_1"]),
        "old_2": resolve_project_path(DEFAULT_OLD_PHOTOS["old_2"]),
        "current_1": resolve_project_path(f"captures/{session_id}/current_1.jpg"),
        "current_2": resolve_project_path(f"captures/{session_id}/current_2.jpg"),
    }


def default_output_path(session_id: str) -> Path:
    return resolve_project_path(f"output/sessions/{session_id}/final.jpg")


def selected_capture_photo_paths(session_id: str, capture_slots: list[int]) -> dict[str, Path]:
    if len(capture_slots) != 4:
        raise ValueError("Exactly 4 capture slots must be selected.")
    if len(set(capture_slots)) != 4:
        raise ValueError("Selected capture slots must be unique.")
    if any(slot < 1 or slot > 8 for slot in capture_slots):
        raise ValueError("Selected capture slots must be 1 to 8.")

    frame_keys = ["old_1", "current_1", "current_2", "old_2"]
    return {
        frame_key: resolve_project_path(f"captures/{session_id}/current_{capture_slot}.jpg")
        for frame_key, capture_slot in zip(frame_keys, capture_slots)
    }


def _paste_image(canvas: Image.Image, image: Image.Image, box: ImageBox) -> None:
    canvas.paste(image, (box.x, box.y))


def _fit_contain(image: Image.Image, width: int, height: int) -> Image.Image:
    fitted = image.copy()
    fitted.thumbnail((width, height), Image.Resampling.LANCZOS)
    return fitted


def _paste_logo(canvas: Image.Image, logo_path: Path, box: ImageBox) -> None:
    if not logo_path.exists():
        return

    with Image.open(logo_path) as logo:
        logo_rgba = logo.convert("RGBA")
        fitted = _fit_contain(logo_rgba, box.width, box.height)
        x = box.x + (box.width - fitted.width) // 2
        y = box.y + (box.height - fitted.height) // 2
        canvas.paste(fitted, (x, y), fitted)


def _paste_overlay(canvas: Image.Image, overlay_path: Path) -> None:
    if not overlay_path.exists():
        return

    with Image.open(overlay_path) as overlay:
        overlay_rgba = overlay.convert("RGBA")
        if overlay_rgba.size != canvas.size:
            overlay_rgba = overlay_rgba.resize(canvas.size, Image.Resampling.LANCZOS)
        canvas.paste(overlay_rgba, (0, 0), overlay_rgba)


def _load_text_font(font_size: int) -> ImageFont.ImageFont:
    for font_path in (
        PROJECT_ROOT / "assets" / "fonts" / "Jua-Regular.ttf",
        Path("C:/Windows/Fonts/NotoSansKR-VF.ttf"),
        Path("C:/Windows/Fonts/malgunbd.ttf"),
        Path("C:/Windows/Fonts/malgun.ttf"),
    ):
        if font_path.exists():
            return ImageFont.truetype(str(font_path), font_size)
    return ImageFont.load_default()


def _draw_text(canvas: Image.Image, text_spec: TextSpec) -> None:
    draw = ImageDraw.Draw(canvas)
    font = _load_text_font(text_spec.font_size)
    bbox = draw.textbbox((0, 0), text_spec.value, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if text_spec.align == "center":
        x = text_spec.x + (text_spec.width - text_width) // 2
    elif text_spec.align == "right":
        x = text_spec.x + text_spec.width - text_width
    else:
        x = text_spec.x
    y = text_spec.y + (text_spec.height - text_height) // 2 - bbox[1]
    draw.text((x, y), text_spec.value, fill=text_spec.color, font=font)


def compose_session(
    session_id: str,
    template_id: str = "default",
    selected_capture_slots: list[int] | None = None,
    photo_paths: dict[str, Path | str] | None = None,
    output_path: Path | str | None = None,
) -> Path:
    from app.services.session_service import validate_session_id, write_session_metadata

    session_id = validate_session_id(session_id)
    template = load_template(template_id)
    resolved_photos = (
        selected_capture_photo_paths(session_id, selected_capture_slots)
        if selected_capture_slots
        else default_photo_paths(session_id)
    )
    if photo_paths:
        resolved_photos.update(
            {key: resolve_project_path(path) for key, path in photo_paths.items()}
        )

    canvas = Image.new(
        "RGB",
        (template.canvas.width, template.canvas.height),
        template.canvas.background,
    )

    for slot in template.slots:
        source_path = resolved_photos.get(slot.key)
        if source_path is None:
            raise FileNotFoundError(f"No source image configured for slot '{slot.key}'.")
        if not source_path.exists():
            raise FileNotFoundError(f"Source image not found for slot '{slot.key}': {source_path}")

        image = load_image(source_path)
        fitted = center_crop_to_size(image, slot.width, slot.height)
        _paste_image(canvas, fitted, slot)

    if template.logo:
        _paste_logo(canvas, resolve_project_path(template.logo.src), template.logo)

    if template.overlay:
        _paste_overlay(canvas, resolve_project_path(template.overlay))

    if template.texts:
        for text_spec in template.texts:
            _draw_text(canvas, text_spec)

    final_path = Path(output_path) if output_path else default_output_path(session_id)
    if not final_path.is_absolute():
        final_path = PROJECT_ROOT / final_path
    final_path.parent.mkdir(parents=True, exist_ok=True)

    canvas.save(final_path, format="JPEG", quality=template.output.quality)

    write_session_metadata(
        session_id,
        status="composed",
        template_id=template_id,
        final_image=final_path,
        old_photos=[],
        captures=[
            f"captures/{session_id}/current_{slot}.jpg"
            for slot in range(1, 9)
            if resolve_project_path(f"captures/{session_id}/current_{slot}.jpg").exists()
        ],
    )
    return final_path
