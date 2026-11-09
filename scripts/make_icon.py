#!/usr/bin/env python3
"""Sinh `installer/app.ico` từ palette TLU (nguồn duy nhất, tái tạo được).

Chạy: python scripts/make_icon.py
Cần Pillow (đã có trong requirements-dev.txt). Chỉ D chạy lại khi đổi logo.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

NAVY = (0, 0, 102, 255)  # #000066
RED = (243, 36, 9, 255)  # #F32409
WHITE = (255, 255, 255, 255)
SIZE = 256
FONT_PATH = Path("assets/fonts/Manrope[wght].ttf")
OUT = Path("installer/app.ico")


def draw_icon(size: int) -> Image.Image:
    """Vẽ icon ở kích thước 256 rồi resize giữ nét."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Nền navy bo góc
    d.rounded_rectangle((0, 0, SIZE - 1, SIZE - 1), radius=56, fill=NAVY)

    # Chữ C trắng — dùng font Manrope, đậm bằng stroke
    try:
        font = ImageFont.truetype(str(FONT_PATH), 176)
    except OSError:
        font = ImageFont.load_default(176)
    box = d.textbbox((0, 0), "C", font=font, stroke_width=6)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(
        ((SIZE - w) / 2 - box[0], (SIZE - h) / 2 - box[1] - 8),
        "C",
        font=font,
        fill=WHITE,
        stroke_width=6,
        stroke_fill=WHITE,
    )

    # Swoosh đỏ đặc trưng TLU
    d.line([(52, 206), (110, 224), (176, 222), (214, 198)], fill=RED, width=14, joint="curve")

    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    sizes = [16, 24, 32, 48, 64, 128, 256]
    frames = [draw_icon(s) for s in sizes]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[-1].save(OUT, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"✅ {OUT} ({OUT.stat().st_size // 1024} KB, {len(sizes)} kích thước)")


if __name__ == "__main__":
    main()
