"""Generate assets/icon.ico — a rounded tile with two opposing convert arrows."""

from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 256
BG = (63, 81, 181)  # indigo
FG = (255, 255, 255)


def draw_icon() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([8, 8, SIZE - 8, SIZE - 8], radius=48, fill=BG)

    # Top arrow pointing right, bottom arrow pointing left.
    def arrow(y: int, flip: bool) -> None:
        shaft = [64, y - 10, 152, y + 10]
        head = [(152, y - 26), (152, y + 26), (196, y)]
        if flip:
            shaft = [SIZE - shaft[2], y - 10, SIZE - shaft[0], y + 10]
            head = [(SIZE - x, hy) for x, hy in head]
        d.rectangle(shaft, fill=FG)
        d.polygon(head, fill=FG)

    arrow(96, flip=False)
    arrow(160, flip=True)
    return img


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
    out.parent.mkdir(exist_ok=True)
    icon = draw_icon()
    icon.save(out, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
