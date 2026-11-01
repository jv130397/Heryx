"""Extract metadata and representative frames from the read-only model video.

Run with PyAV available (the audit used an isolated ``pip --target`` directory).
"""

from __future__ import annotations

import json
from pathlib import Path

import av
from PySide6.QtGui import QImage

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Modelos" / "heredograma_linkedin.mp4"
OUTPUT = ROOT / "specifications" / "assets" / "model_reference"


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    container = av.open(str(SOURCE))
    stream = container.streams.video[0]
    duration_seconds = float(stream.duration * stream.time_base)
    targets = [duration_seconds * index / 8 for index in range(9)]
    captured: list[dict[str, int | float | str]] = []
    target_index = 0
    for frame in container.decode(stream):
        if frame.time is None or frame.time + 0.02 < targets[target_index]:
            continue
        rgba = frame.reformat(format="rgba")
        plane = rgba.planes[0]
        image = QImage(
            bytes(plane),
            rgba.width,
            rgba.height,
            plane.line_size,
            QImage.Format.Format_RGBA8888,
        ).copy()
        position_ms = round(float(frame.time) * 1000)
        path = OUTPUT / f"frame_{target_index:02d}_{position_ms:06d}ms.png"
        image.save(str(path))
        captured.append(
            {
                "position_ms": position_ms,
                "path": str(path.relative_to(ROOT)),
                "width": image.width(),
                "height": image.height(),
            }
        )
        target_index += 1
        if target_index == len(targets):
            break
    result = {
        "source": str(SOURCE.relative_to(ROOT)),
        "duration_ms": round(duration_seconds * 1000),
        "file_size_bytes": SOURCE.stat().st_size,
        "codec": stream.codec_context.name,
        "pixel_format": stream.codec_context.format.name,
        "video_resolution": [stream.width, stream.height],
        "average_frame_rate": str(stream.average_rate),
        "frames": captured,
    }
    (OUTPUT / "metadata.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
