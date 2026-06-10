"""Image loading, EXIF correction, and crop helpers."""

from pathlib import Path

from PIL import Image, ImageOps


def load_image(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).convert("RGB")


def center_crop_to_size(image: Image.Image, width: int, height: int) -> Image.Image:
    source_width, source_height = image.size
    target_ratio = width / height
    source_ratio = source_width / source_height

    if source_ratio > target_ratio:
        crop_height = source_height
        crop_width = round(crop_height * target_ratio)
        left = (source_width - crop_width) // 2
        top = 0
    else:
        crop_width = source_width
        crop_height = round(crop_width / target_ratio)
        left = 0
        top = (source_height - crop_height) // 2

    cropped = image.crop((left, top, left + crop_width, top + crop_height))
    return cropped.resize((width, height), Image.Resampling.LANCZOS)
