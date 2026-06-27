#!/usr/bin/env python3
"""Generate NothingOS-inspired dot-matrix "H" icons (favicon + apple-touch).

Draws a 5x5 dot-matrix H: light dots on a solid dark rounded tile, with one
red accent dot at the centre. Solid background is required so iOS home-screen
icons (Add to Home Screen) render correctly instead of going transparent/black.

Renders each target at 4x supersample then downscales for clean antialiasing.
"""
from PIL import Image, ImageDraw

OUT = "static"

BG = (11, 11, 10, 255)        # #0b0b0a  NothingOS surface
DOT = (242, 240, 232, 255)    # #f2f0e8  light ink
RED = (255, 59, 48, 255)      # #ff3b30  single accent

# Dot-matrix H on a 64-unit grid: two vertical bars (cols 16/48, rows 16..48)
# plus the centre crossbar (24,32)-(40,32). Centre (32,32) is the red accent.
COLS = [16, 48]
ROWS = [16, 24, 32, 40, 48]
H_DOTS = [(c, r) for c in COLS for r in ROWS]
H_DOTS += [(24, 32), (40, 32)]
RED_DOT = (32, 32)
DOT_R = 3.4          # radius in grid units
RADIUS = 12 / 64     # corner radius as fraction of side


def render(size: int) -> Image.Image:
    ss = 4
    px = size * ss
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded solid tile.
    r = RADIUS * px
    d.rounded_rectangle([0, 0, px - 1, px - 1], radius=r, fill=BG)

    scale = px / 64.0
    rad = DOT_R * scale

    def dot(cx, cy, color):
        x, y = cx * scale, cy * scale
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=color)

    for cx, cy in H_DOTS:
        dot(cx, cy, DOT)
    dot(*RED_DOT, RED)

    return img.resize((size, size), Image.LANCZOS)


def main():
    targets = {
        "favicon-32.png": 32,
        "favicon-192.png": 192,
        "favicon-512.png": 512,
        "apple-touch-icon.png": 512,
    }
    rendered = {}
    for name, size in targets.items():
        im = render(size)
        im.save(f"{OUT}/{name}")
        rendered[size] = im
        print(f"wrote {OUT}/{name} ({size}x{size})")

    # Multi-resolution .ico (16 + 32) from the 512 master for crispness.
    master = render(256)
    master.save(f"{OUT}/favicon.ico", sizes=[(16, 16), (32, 32)])
    print(f"wrote {OUT}/favicon.ico (16,32)")


if __name__ == "__main__":
    main()
