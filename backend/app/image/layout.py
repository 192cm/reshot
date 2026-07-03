"""Frame layout models used by image composition."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CanvasSpec:
    width: int
    height: int
    background: str


@dataclass(frozen=True)
class ImageBox:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class SlotSpec(ImageBox):
    key: str


@dataclass(frozen=True)
class LogoSpec(ImageBox):
    src: str
    fit: str = "contain"


@dataclass(frozen=True)
class TextSpec(ImageBox):
    value: str
    color: str = "#ffffff"
    font_size: int = 32
    align: str = "right"


@dataclass(frozen=True)
class OutputSpec:
    format: str = "jpg"
    quality: int = 92


@dataclass(frozen=True)
class FrameTemplate:
    id: str
    canvas: CanvasSpec
    slots: list[SlotSpec]
    output: OutputSpec
    logo: LogoSpec | None = None
    overlay: str | None = None
    texts: list[TextSpec] | None = None


def _require_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"Template field '{key}' must be a positive integer.")
    return value


def box_from_dict(data: dict[str, Any]) -> ImageBox:
    return ImageBox(
        x=_require_int(data, "x"),
        y=_require_int(data, "y"),
        width=_require_int(data, "width"),
        height=_require_int(data, "height"),
    )


def template_from_dict(data: dict[str, Any]) -> FrameTemplate:
    canvas_data = data.get("canvas")
    if not isinstance(canvas_data, dict):
        raise ValueError("Template must include a canvas object.")

    background = canvas_data.get("background")
    if not isinstance(background, str) or not background:
        raise ValueError("Template canvas.background must be a non-empty string.")

    slots_data = data.get("slots")
    if not isinstance(slots_data, list) or not slots_data:
        raise ValueError("Template must include one or more slots.")

    slots: list[SlotSpec] = []
    for slot_data in slots_data:
        if not isinstance(slot_data, dict):
            raise ValueError("Each template slot must be an object.")
        key = slot_data.get("key")
        if not isinstance(key, str) or not key:
            raise ValueError("Each template slot must include a non-empty key.")
        box = box_from_dict(slot_data)
        slots.append(SlotSpec(key=key, x=box.x, y=box.y, width=box.width, height=box.height))

    output_data = data.get("output") or {}
    if not isinstance(output_data, dict):
        raise ValueError("Template output must be an object when provided.")

    logo = None
    logo_data = data.get("logo")
    if isinstance(logo_data, dict):
        src = logo_data.get("src")
        if not isinstance(src, str) or not src:
            raise ValueError("Template logo.src must be a non-empty string.")
        logo_box = box_from_dict(logo_data)
        fit = logo_data.get("fit", "contain")
        if not isinstance(fit, str):
            raise ValueError("Template logo.fit must be a string.")
        logo = LogoSpec(
            src=src,
            x=logo_box.x,
            y=logo_box.y,
            width=logo_box.width,
            height=logo_box.height,
            fit=fit,
        )

    texts = []
    texts_data = data.get("texts") or []
    if not isinstance(texts_data, list):
        raise ValueError("Template texts must be a list when provided.")
    for text_data in texts_data:
        if not isinstance(text_data, dict):
            raise ValueError("Each template text must be an object.")
        value = text_data.get("value")
        if not isinstance(value, str) or not value:
            raise ValueError("Each template text must include a non-empty value.")
        text_box = box_from_dict(text_data)
        color = text_data.get("color", "#ffffff")
        align = text_data.get("align", "right")
        font_size = text_data.get("font_size", 32)
        if not isinstance(color, str) or not color:
            raise ValueError("Template text color must be a string.")
        if align not in {"left", "center", "right"}:
            raise ValueError("Template text align must be left, center, or right.")
        if not isinstance(font_size, int) or font_size <= 0:
            raise ValueError("Template text font_size must be a positive integer.")
        texts.append(TextSpec(
            value=value,
            x=text_box.x,
            y=text_box.y,
            width=text_box.width,
            height=text_box.height,
            color=color,
            font_size=font_size,
            align=align,
        ))

    template_id = data.get("id")
    if not isinstance(template_id, str) or not template_id:
        raise ValueError("Template id must be a non-empty string.")

    overlay = data.get("overlay")
    if overlay is not None and not isinstance(overlay, str):
        raise ValueError("Template overlay must be a string when provided.")

    return FrameTemplate(
        id=template_id,
        canvas=CanvasSpec(
            width=_require_int(canvas_data, "width"),
            height=_require_int(canvas_data, "height"),
            background=background,
        ),
        slots=slots,
        logo=logo,
        overlay=overlay,
        texts=texts,
        output=OutputSpec(
            format=str(output_data.get("format", "jpg")),
            quality=int(output_data.get("quality", 92)),
        ),
    )
