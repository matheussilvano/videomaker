"""`videomaker setup`: narration models, a browser, and the pinned upstream skills."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .media import MediaError
from .tts import MODEL_FILES, home_dir, models_dir


@dataclass(frozen=True)
class Upstream:
    link_name: str
    repo: str
    commit: str
    subdir: str = ""
    uv_sync: bool = False


# Pinned: setup never follows a moving branch. Bump these on purpose, after reading the diff.
UPSTREAM = [
    Upstream("video-use", "https://github.com/browser-use/video-use.git",
             "43cfc566833548093455c9d4a46bd69913b7e552", uv_sync=True),
    Upstream("motion-design", "https://github.com/howseen-ai/claude-motion-design.git",
             "3d90d349ef3fdde9b7e89de4df4a2159c9e8697f", subdir="skill/motion-design"),
]  # fmt: skip


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def install_models() -> None:
    models_dir().mkdir(parents=True, exist_ok=True)
    for name, (url, sha) in MODEL_FILES.items():
        dest = models_dir() / name
        if dest.is_file() and _sha256(dest) == sha:
            print(f"model ok: {name}")
            continue
        print(f"downloading {name} ...")
        part = dest.with_suffix(dest.suffix + ".part")
        with urllib.request.urlopen(url) as resp, part.open("wb") as out:  # noqa: S310
            shutil.copyfileobj(resp, out)
        if _sha256(part) != sha:
            part.unlink()
            raise MediaError(f"checksum mismatch for {name}; refusing to use it")
        part.replace(dest)
        print(f"model ok: {name}")


def install_browser() -> None:
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)


def _git(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(["git", *args], check=True, cwd=cwd, capture_output=True, text=True)


def install_skills(claude_skills: Path | None = None) -> None:
    skills = claude_skills or Path("~/.claude/skills").expanduser()
    skills.mkdir(parents=True, exist_ok=True)
    base = home_dir() / "upstream"
    base.mkdir(parents=True, exist_ok=True)
    for up in UPSTREAM:
        link = skills / up.link_name
        if link.exists() or link.is_symlink():
            print(f"skill present, left alone: {link}")
            continue
        repo_dir = base / up.link_name
        if not repo_dir.exists():
            print(f"cloning {up.repo} @ {up.commit[:8]}")
            repo_dir.mkdir(parents=True)
            _git("init", "-q", cwd=repo_dir)
            _git("remote", "add", "origin", up.repo, cwd=repo_dir)
            _git("fetch", "-q", "--depth", "1", "origin", up.commit, cwd=repo_dir)
            _git("checkout", "-q", "FETCH_HEAD", cwd=repo_dir)
        if up.uv_sync and shutil.which("uv"):
            print(f"installing dependencies for {up.link_name} (uv sync) ...")
            subprocess.run(["uv", "sync", "-q"], cwd=repo_dir, check=True)
        link.symlink_to(repo_dir / up.subdir if up.subdir else repo_dir)
        print(f"linked {link}")
