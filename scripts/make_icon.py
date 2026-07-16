"""Generate the app icons — assets/icon.ico (Windows) and assets/icon.icns
(macOS): a rounded tile with two opposing convert arrows."""

from pathlib import Path

from PIL import Image, ImageDraw

BASE = 1024  # draw large once, downscale for each icon size
BG = (63, 81, 181)  # indigo
FG = (255, 255, 255)


def draw_icon(size: int = BASE) -> Image.Image:
    s = size / 256  # coordinates below are designed on a 256 grid
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([8 * s, 8 * s, size - 8 * s, size - 8 * s], radius=48 * s, fill=BG)

    # Top arrow pointing right, bottom arrow pointing left.
    def arrow(y: float, flip: bool) -> None:
        shaft = [64 * s, (y - 10) * s, 152 * s, (y + 10) * s]
        head = [(152 * s, (y - 26) * s), (152 * s, (y + 26) * s), (196 * s, y * s)]
        if flip:
            shaft = [size - shaft[2], shaft[1], size - shaft[0], shaft[3]]
            head = [(size - x, hy) for x, hy in head]
        d.rectangle(shaft, fill=FG)
        d.polygon(head, fill=FG)

    arrow(96, flip=False)
    arrow(160, flip=True)
    return img


def main() -> None:
    assets = Path(__file__).resolve().parent.parent / "assets"
    assets.mkdir(exist_ok=True)
    icon = draw_icon()

    sizes = [16, 32, 48, 64, 128, 256]
    icon.resize((256, 256), Image.LANCZOS).save(
        assets / "icon.ico", sizes=[(n, n) for n in sizes]
    )
    icon.save(
        assets / "icon.icns",
        append_images=[icon.resize((n, n), Image.LANCZOS) for n in (512, 256, 128, 64, 32, 16)],
    )
    print(f"wrote {assets / 'icon.ico'} and {assets / 'icon.icns'}")


if __name__ == "__main__":
    main()
