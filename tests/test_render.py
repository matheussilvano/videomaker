"""End-to-end checks that need ffmpeg and a browser. Skipped where they are missing."""

import json
import shutil
from pathlib import Path

import pytest

from videomaker.assemble import build, still
from videomaker.media import duration_of

pytestmark = pytest.mark.browser

needs_tools = pytest.mark.skipif(
    not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="ffmpeg not installed"
)


def _browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        from videomaker.render import launch_browser

        with sync_playwright() as p:
            launch_browser(p).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_available(), reason="no Chromium/Chrome")

SMALL = {
    "format": {"width": 270, "height": 480, "fps": 10},
    "voice": {"engine": "none"},
    "captions": {"enabled": True, "style": "impact"},
    "hud": {"badge": "1", "title": "TEST"},
    "scenes": [
        {"id": "a", "type": "title", "text": "Hello world", "duration": 1.0},
        {"id": "b", "type": "story", "pose": "wave", "headline": "Hi", "duration": 1.0,
         "narration": "two words", "caption_text": "Two words"},
        {"id": "c", "type": "stat", "value": "90%", "label": "done", "duration": 0.5},
    ],
}  # fmt: skip


@needs_tools
@needs_browser
def test_build_makes_a_video_of_the_planned_length(tmp_path: Path):
    sb = tmp_path / "sb.json"
    sb.write_text(json.dumps(SMALL))
    logs: list[str] = []
    final = build(sb, tmp_path / "out", log=logs.append)
    assert final.name == "final.mp4"
    planned = json.loads((tmp_path / "out" / "storyboard.resolved.json").read_text())[
        "total_seconds"
    ]
    assert abs(duration_of(final) - planned) < 0.3
    assert (tmp_path / "out" / "captions.srt").exists()

    logs.clear()
    build(sb, tmp_path / "out", log=logs.append)  # second run: every scene comes from the cache
    assert sum("cached" in line for line in logs) == 3


@needs_tools
@needs_browser
def test_still_writes_a_png(tmp_path: Path):
    sb = tmp_path / "sb.json"
    sb.write_text(json.dumps(SMALL))
    png = still(sb, tmp_path / "out", "b", 0.5, log=lambda _: None)
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
