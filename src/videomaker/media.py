"""Thin ffmpeg/ffprobe helpers."""

from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

# One encoding recipe for every segment, so the final join can be a lossless `-c copy`.
VIDEO_ARGS = [
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p",
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
]  # fmt: skip
AUDIO_ARGS = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


class MediaError(RuntimeError):
    """ffmpeg or ffprobe failed; the message carries the tail of its stderr."""


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise MediaError(
            f"{name} not found on PATH. Install ffmpeg (e.g. `sudo apt install ffmpeg`)."
        )
    return path


def run_ffmpeg(args: Sequence[str | Path], *, cwd: Path | None = None) -> None:
    cmd = [require_tool("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error", *map(str, args)]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-12:])
        raise MediaError(f"ffmpeg failed ({proc.returncode}):\n{tail}")


def probe(path: Path) -> dict[str, object]:
    proc = subprocess.run(
        [
            require_tool("ffprobe"),
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise MediaError(f"ffprobe could not read {path}: {proc.stderr.strip()[-300:]}")
    data: dict[str, object] = json.loads(proc.stdout)
    return data


def duration_of(path: Path) -> float:
    fmt = probe(path).get("format")
    if not isinstance(fmt, dict) or "duration" not in fmt:
        raise MediaError(f"no duration in {path}")
    return float(fmt["duration"])


def has_audio(path: Path) -> bool:
    streams = probe(path).get("streams")
    return isinstance(streams, list) and any(
        isinstance(s, dict) and s.get("codec_type") == "audio" for s in streams
    )


def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTS
