from pathlib import Path

import pytest
from PIL import Image

from fileconv.images import convert_image


@pytest.fixture
def sample_png(tmp_path: Path) -> Path:
    path = tmp_path / "sample.png"
    Image.new("RGB", (64, 48), (200, 60, 30)).save(path)
    return path


@pytest.fixture
def sample_rgba_png(tmp_path: Path) -> Path:
    path = tmp_path / "alpha.png"
    Image.new("RGBA", (64, 48), (0, 120, 255, 128)).save(path)
    return path


@pytest.mark.parametrize("target", ["jpg", "webp", "bmp", "tiff", "gif", "heic"])
def test_png_to_others(sample_png: Path, tmp_path: Path, target: str):
    dest = convert_image(sample_png, tmp_path / f"out.{target}")
    assert dest.exists() and dest.stat().st_size > 0
    with Image.open(dest) as img:
        assert img.size == (64, 48)


def test_heic_round_trip(sample_png: Path, tmp_path: Path):
    heic = convert_image(sample_png, tmp_path / "mid.heic")
    jpg = convert_image(heic, tmp_path / "back.jpg")
    with Image.open(jpg) as img:
        assert img.format == "JPEG"
        assert img.size == (64, 48)


def test_alpha_flattened_for_jpeg(sample_rgba_png: Path, tmp_path: Path):
    dest = convert_image(sample_rgba_png, tmp_path / "flat.jpg")
    with Image.open(dest) as img:
        assert img.mode == "RGB"


def test_png_keeps_alpha_via_webp(sample_rgba_png: Path, tmp_path: Path):
    webp = convert_image(sample_rgba_png, tmp_path / "keep.webp")
    with Image.open(webp) as img:
        assert "A" in img.mode
