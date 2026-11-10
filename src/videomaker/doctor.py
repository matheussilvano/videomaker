"""`videomaker doctor`: what works on this machine and what is missing."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .tts import models_dir, models_ready


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    required: bool = True


def _ffmpeg_has(kind: str, name: str) -> bool:
    out = subprocess.run(["ffmpeg", "-hide_banner", f"-{kind}"], capture_output=True, text=True)
    return any(name in line.split() for line in out.stdout.splitlines())


def _browser() -> Check:
    try:
        from playwright.sync_api import sync_playwright

        from .render import launch_browser

        with sync_playwright() as p:
            b = launch_browser(p)
            version = b.version
            b.close()
        return Check("browser", True, f"Chromium/Chrome {version}")
    except Exception as exc:
        return Check("browser", False, f"{str(exc)[:140]} -> `videomaker setup --browser`")


def run_checks() -> list[Check]:
    checks: list[Check] = []
    have_ffmpeg = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
    checks.append(
        Check("ffmpeg + ffprobe", have_ffmpeg, "on PATH" if have_ffmpeg else "install ffmpeg")
    )
    if have_ffmpeg:
        for kind, name in (("encoders", "libx264"), ("filters", "ass"), ("filters", "loudnorm")):
            ok = _ffmpeg_has(kind, name)
            checks.append(
                Check(f"ffmpeg {name}", ok, "ok" if ok else "missing in this ffmpeg build")
            )
    checks.append(_browser())
    checks.append(
        Check(
            "narration models",
            models_ready(),
            str(models_dir()) if models_ready() else "run `videomaker setup --models`",
            required=False,
        )
    )
    asr = importlib.util.find_spec("faster_whisper") is not None
    checks.append(
        Check("local transcription", asr, "faster-whisper" if asr else "uv sync --extra asr", False)
    )
    skills = Path("~/.claude/skills").expanduser()
    for name, label in (
        ("video-use", "video-use (edit footage)"),
        ("motion-design", "motion-design"),
    ):
        ok = (skills / name / "SKILL.md").is_file()
        checks.append(
            Check(label, ok, "installed" if ok else "run `videomaker setup --skills`", False)
        )
    return checks


def report(checks: list[Check]) -> int:
    for c in checks:
        mark = "ok  " if c.ok else ("FAIL" if c.required else "skip")
        print(f"[{mark}] {c.name}: {c.detail}")
    failed = [c for c in checks if c.required and not c.ok]
    print("\nReady." if not failed else f"\n{len(failed)} required check(s) failed.")
    return 1 if failed else 0
