"""Image format conversions built on Pillow (+ pillow-heif for HEIC/HEIF)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

# extension -> Pillow format name
IMAGE_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "heic": "HEIF",
    "heif": "HEIF",
    "webp": "WEBP",
    "bmp": "BMP",
    "tif": "TIFF",
    "tiff": "TIFF",
    "gif": "GIF",
    "ico": "ICO",
}

# Formats that cannot store an alpha channel.
_NO_ALPHA = {"JPEG", "BMP"}
# Formats that can carry EXIF metadata.
_EXIF_OK = {"JPEG", "HEIF", "WEBP", "TIFF", "PNG"}


def is_image_ext(ext: str) -> bool:
    return ext.lower().lstrip(".") in IMAGE_FORMATS


def convert_image(src: Path, dest: Path, quality: int = 90) -> Path:
    """Convert a single image file. Preserves EXIF and ICC profile when the
    target format supports them, and flattens alpha for formats that don't."""
    target = IMAGE_FORMATS[dest.suffix.lstrip(".").lower()]

    with Image.open(src) as img:
        save_kwargs: dict = {}

        exif = img.info.get("exif")
        if exif and target in _EXIF_OK:
            save_kwargs["exif"] = exif
        icc = img.info.get("icc_profile")
        if icc:
            save_kwargs["icc_profile"] = icc

        if img.mode == "P":
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")
        if target in _NO_ALPHA and img.mode not in ("RGB", "L"):
            # Composite transparency onto white instead of dropping the channel.
            if "A" in img.mode:
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.getchannel("A"))
                img = background
            else:
                img = img.convert("RGB")

        if target in {"JPEG", "WEBP", "HEIF"}:
            save_kwargs["quality"] = quality

        img.save(dest, format=target, **save_kwargs)

    return dest
