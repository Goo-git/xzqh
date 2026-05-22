#!/usr/bin/env python3
"""Generate xzqh app icons (PNG + multi-size ICO) using Pillow.

Idempotent. Run any time to regen ``assets/icon.png`` and ``assets/icon.ico``.
For macOS ``.icns``, see ``.github/workflows/build-app.yml`` — it generates
icns at CI time using ``iconutil`` on the macOS runner.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024
OUT_DIR = Path(__file__).resolve().parent.parent / "assets"

# Gradient endpoints — deep indigo top-left → vivid blue bottom-right.
GRAD_FROM = (54, 71, 184)
GRAD_TO = (76, 139, 245)
GLYPH_COLOR = (255, 255, 255)
ACCENT_COLOR = (229, 75, 75)


def make_gradient(size: int) -> Image.Image:
    """Diagonal gradient in linear RGB."""
    img = Image.new("RGB", (size, size), GRAD_FROM)
    draw = ImageDraw.Draw(img)
    diag = math.sqrt(2 * size * size)
    for y in range(size):
        for x_start in (0,):  # one line per y is enough using full-width fill
            # blend factor based on (x+y)/(size*2) so the gradient is diagonal
            # we approximate by drawing horizontal bands with diagonal-correct color.
            pass
    # Faster: per-row diagonal approximation using two-tone interpolation.
    for d in range(size + size):  # diagonal index 0..2*size
        t = d / (2 * (size - 1))
        r = int(round(GRAD_FROM[0] * (1 - t) + GRAD_TO[0] * t))
        g = int(round(GRAD_FROM[1] * (1 - t) + GRAD_TO[1] * t))
        b = int(round(GRAD_FROM[2] * (1 - t) + GRAD_TO[2] * t))
        # All pixels (x, y) where x+y == d
        x0 = max(0, d - (size - 1))
        x1 = min(size - 1, d)
        # The line from (x0, d-x0) to (x1, d-x1) is one diagonal stride
        draw.line([(x0, d - x0), (x1, d - x1)], fill=(r, g, b))
    return img


def rounded_mask(size: int, radius_ratio: float = 0.22) -> Image.Image:
    radius = int(size * radius_ratio)
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([(0, 0), (size - 1, size - 1)], radius=radius, fill=255)
    return mask


def draw_glyph(canvas: Image.Image) -> None:
    """Draw a stylized 'x' geometric mark + accent dot."""
    size = canvas.size[0]
    cx = cy = size // 2
    arm = int(size * 0.30)
    thickness = int(size * 0.085)

    # Build the X on a transparent layer, then composite with slight glow.
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    # Two crossing rounded-rectangle strokes (rotated 45° each).
    def stroke(angle_deg: float) -> None:
        from math import cos, radians, sin

        a = radians(angle_deg)
        dx, dy = cos(a) * arm, sin(a) * arm
        # Rectangle endpoints (the stroke goes from -arm to +arm along the angle).
        # Compute four corners of an oriented capsule by offsetting perpendicular.
        px, py = -sin(a) * thickness / 2, cos(a) * thickness / 2
        pts = [
            (cx - dx + px, cy - dy + py),
            (cx + dx + px, cy + dy + py),
            (cx + dx - px, cy + dy - py),
            (cx - dx - px, cy - dy - py),
        ]
        ld.polygon(pts, fill=GLYPH_COLOR)
        # round caps
        ld.ellipse(
            [(cx - dx - thickness / 2, cy - dy - thickness / 2),
             (cx - dx + thickness / 2, cy - dy + thickness / 2)],
            fill=GLYPH_COLOR,
        )
        ld.ellipse(
            [(cx + dx - thickness / 2, cy + dy - thickness / 2),
             (cx + dx + thickness / 2, cy + dy + thickness / 2)],
            fill=GLYPH_COLOR,
        )

    stroke(45)
    stroke(-45)

    # Accent dot — bottom-right, like a status indicator.
    r = int(size * 0.075)
    cx2 = int(size * 0.77)
    cy2 = int(size * 0.77)
    ld.ellipse(
        [(cx2 - r, cy2 - r), (cx2 + r, cy2 + r)],
        fill=ACCENT_COLOR,
    )

    # Subtle drop shadow for depth.
    shadow = layer.split()[3].filter(ImageFilter.GaussianBlur(radius=size * 0.012))
    canvas.paste((0, 0, 0), mask=Image.eval(shadow, lambda v: int(v * 0.45)))

    canvas.paste(layer, mask=layer)


def build_icon() -> Image.Image:
    base = make_gradient(SIZE).convert("RGBA")
    mask = rounded_mask(SIZE)
    # Apply rounded mask
    rounded = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    rounded.paste(base, mask=mask)
    draw_glyph(rounded)
    return rounded


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    icon = build_icon()
    png_path = OUT_DIR / "icon.png"
    ico_path = OUT_DIR / "icon.ico"
    icon.save(png_path, "PNG", optimize=True)
    # Multi-size ICO: Windows picks the best size at runtime.
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
             (128, 128), (256, 256)]
    icon.save(ico_path, format="ICO", sizes=sizes)
    print(f"wrote {png_path}")
    print(f"wrote {ico_path}  (sizes={sizes})")


if __name__ == "__main__":
    main()
