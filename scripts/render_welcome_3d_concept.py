"""Render a short 2.5D concept video from the approved Welcome mockup."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/phase_4_16_0/concepts/welcome-3d-base.png"
TARGET = ROOT / "assets/phase_4_16_0/concepts/welcome-3d-motion-concept.mp4"
WIDTH, HEIGHT = 1280, 720
FPS = 24
DURATION = 8.0


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return 1.0 - (1.0 - value) ** 3


def interval(time: float, start: float, end: float) -> float:
    return ease((time - start) / (end - start))


def feathered_box(box: tuple[int, int, int, int], feather: int = 34) -> Image.Image:
    mask = Image.new("L", (WIDTH, HEIGHT))
    ImageDraw.Draw(mask).rectangle(box, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(feather))


def transformed_layer(
    image: Image.Image,
    box: tuple[int, int, int, int],
    scale: float,
    angle: float,
    offset: tuple[int, int],
) -> Image.Image:
    crop = image.crop(box)
    size = (round(crop.width * scale), round(crop.height * scale))
    crop = crop.resize(size, Image.Resampling.LANCZOS)
    crop = crop.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    layer = Image.new("RGB", (WIDTH, HEIGHT), "#081322")
    x = box[0] + (box[2] - box[0] - crop.width) // 2 + offset[0]
    y = box[1] + (box[3] - box[1] - crop.height) // 2 + offset[1]
    layer.paste(crop, (x, y))
    return layer


def render_frame(final: Image.Image, time: float) -> Image.Image:
    backdrop = final.filter(ImageFilter.GaussianBlur(12))
    backdrop = ImageEnhance.Brightness(backdrop).enhance(0.28)
    frame = backdrop.copy()
    frame.paste(final.crop((0, 0, WIDTH, 63)), (0, 0))

    brand_alpha = interval(time, 0.15, 1.15)
    left_alpha = interval(time, 0.75, 2.15)
    recent_alpha = interval(time, 1.35, 2.7)
    left_mask = feathered_box((35, 65, 625, 475))
    left_mask = left_mask.point(lambda pixel: round(pixel * left_alpha))
    left = transformed_layer(final, (30, 60, 670, 490), 0.975 + 0.025 * left_alpha, 0, (0, 8))
    frame.paste(left, mask=left_mask)
    brand_mask = feathered_box((40, 60, 590, 190), 20)
    brand_mask = brand_mask.point(lambda pixel: round(pixel * brand_alpha))
    frame.paste(final, mask=brand_mask)
    recent_mask = feathered_box((45, 430, 650, 650), 24)
    recent_mask = recent_mask.point(lambda pixel: round(pixel * recent_alpha))
    frame.paste(final, mask=recent_mask)

    pedigree_alpha = interval(time, 1.15, 3.65)
    settle = interval(time, 2.0, 4.8)
    idle = math.sin(max(0.0, time - 4.2) * 1.25)
    right = transformed_layer(
        final,
        (650, 65, WIDTH, HEIGHT),
        0.91 + 0.09 * settle,
        -1.4 * (1.0 - settle),
        (round(34 * (1.0 - settle) + idle * 3), round(-12 * (1.0 - settle) + idle * 2)),
    )
    wipe = min(WIDTH, round(610 + pedigree_alpha * 720))
    right_mask = feathered_box((590, 55, wipe, HEIGHT), 42)
    right_mask = right_mask.point(lambda pixel: round(pixel * pedigree_alpha))
    frame.paste(right, mask=right_mask)

    pulse_time = max(0.0, time - 3.1)
    pulse = math.exp(-pulse_time * 0.85) * (0.5 + 0.5 * math.sin(pulse_time * 7.0))
    if pulse > 0.02:
        glow = Image.new("RGBA", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(glow)
        radius = round(34 + pulse * 22)
        center = (884 + round(idle * 3), 433 + round(idle * 2))
        draw.ellipse(
            (
                center[0] - radius,
                center[1] - radius,
                center[0] + radius,
                center[1] + radius,
            ),
            fill=(116, 91, 255, round(105 * pulse)),
        )
        glow = glow.filter(ImageFilter.GaussianBlur(22))
        frame = Image.alpha_composite(frame.convert("RGBA"), glow).convert("RGB")

    if time > 5.1:
        final_mix = interval(time, 5.1, 6.0) * 0.38
        breathing = (math.sin((time - 5.1) * 1.1) + 1.0) * 0.025
        frame = Image.blend(frame, final, min(0.48, final_mix + breathing))
    return frame


def main() -> None:
    dependency_path = Path("/tmp/rarepedigree-video-deps")
    sys.path.insert(0, str(dependency_path))
    import imageio_ffmpeg

    final = Image.open(SOURCE).convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    writer = imageio_ffmpeg.write_frames(
        str(TARGET),
        (WIDTH, HEIGHT),
        fps=FPS,
        codec="libx264",
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        quality=7,
        output_params=["-movflags", "+faststart"],
    )
    writer.send(None)
    try:
        for index in range(round(FPS * DURATION)):
            writer.send(np.asarray(render_frame(final, index / FPS), dtype=np.uint8).tobytes())
    finally:
        writer.close()
    print(TARGET)


if __name__ == "__main__":
    main()
