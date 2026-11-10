import shutil
from pathlib import Path

import pytest


@pytest.fixture
def storyboard_file(tmp_path: Path):
    """Write a storyboard dict to tmp_path/storyboard.json and return its path."""
    import json

    def write(data: dict) -> Path:
        path = tmp_path / "storyboard.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    return write


def have_ffmpeg() -> bool:
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
