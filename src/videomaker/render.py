"""Render generated scenes: HTML + Playwright screenshots piped into ffmpeg.

Every built-in scene is a pure function of time (`window.seek(t)`), so the same
storyboard always produces the same frames, and one scene can be re-rendered alone.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from types import TracebackType
from typing import Any

from playwright.sync_api import Browser, Playwright, sync_playwright

from .media import VIDEO_ARGS, MediaError, require_tool
from .storyboard import Format, HtmlScene, Style

TEMPLATES = Path(__file__).parent / "templates"


def template_version() -> str:
    """Hash of every template file: changing a template invalidates cached scenes."""
    h = hashlib.sha256()
    for p in sorted(TEMPLATES.iterdir()):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def _script_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


FONT_FACES = (
    "@font-face{{font-family:'Anton';src:url('{anton}');}}"
    "@font-face{{font-family:'Montserrat';src:url('{mont}');font-weight:100 900;}}"
)


def font_css() -> str:
    fonts = Path(__file__).parent / "fonts"
    return FONT_FACES.format(
        anton=(fonts / "Anton-Regular.ttf").as_uri(),
        mont=(fonts / "Montserrat[wght].ttf").as_uri().replace("[", "%5B").replace("]", "%5D"),
    )


def build_page(
    scene_type: str,
    scene: dict[str, Any],
    style: Style,
    duration: float,
    extra: dict[str, Any] | None = None,
) -> str:
    """HTML for a built-in scene type. `extra` becomes window.<KEY> globals (HUD, CHARACTER, FPS)."""
    globals_js = "".join(f"window.{k}={_script_json(v)};" for k, v in (extra or {}).items())
    css = (TEMPLATES / "base.css").read_text(encoding="utf-8")
    base = (TEMPLATES / "base.js").read_text(encoding="utf-8")
    body = (TEMPLATES / f"{scene_type}.js").read_text(encoding="utf-8")
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{font_css()}{css}</style></head><body><div id='stage'></div>"
        f"<script>window.SCENE={_script_json(scene)};window.STYLE={_script_json(style.model_dump())};"
        f"window.DURATION={duration};{globals_js}</script>"
        f"<script>{base}</script><script>{body}</script></body></html>"
    )


def launch_browser(p: Playwright) -> Browser:
    """Bundled Chromium first, then the system Chrome, then a clear error."""
    try:
        return p.chromium.launch()
    except Exception as bundled_error:
        try:
            return p.chromium.launch(channel="chrome")
        except Exception:
            raise MediaError(
                "No browser available. Run `videomaker setup --browser` "
                f"(or install Google Chrome). Details: {str(bundled_error)[:160]}"
            ) from None


class Renderer:
    """Keeps one browser open across scenes."""

    def __init__(self, fmt: Format, extra: dict[str, Any] | None = None) -> None:
        self.fmt = fmt
        self.extra = {"FPS": fmt.fps, **(extra or {})}
        self._pw: Playwright | None = None
        self._browser: Browser | None = None

    def __enter__(self) -> Renderer:
        self._pw = sync_playwright().start()
        self._browser = launch_browser(self._pw)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def _open(
        self,
        scene_type: str,
        scene: dict[str, Any],
        style: Style,
        duration: float,
        html_file: Path | None,
        workdir: Path,
    ) -> Any:
        assert self._browser is not None
        page = self._browser.new_page(
            viewport={"width": self.fmt.width, "height": self.fmt.height}, device_scale_factor=1
        )
        if html_file is not None:
            page.add_init_script(
                f"window.SCENE={_script_json(scene)};window.STYLE={_script_json(style.model_dump())};"
                f"window.DURATION={duration};"
                + "".join(f"window.{k}={_script_json(v)};" for k, v in self.extra.items())
            )
            page.goto(html_file.resolve().as_uri())
        else:
            page_file = (
                workdir / f".page-{scene_type}-{abs(hash(json.dumps(scene, sort_keys=True)))}.html"
            )
            page_file.write_text(
                build_page(scene_type, scene, style, duration, self.extra), encoding="utf-8"
            )
            try:
                page.goto(page_file.resolve().as_uri())
            finally:
                page_file.unlink(missing_ok=True)
        page.evaluate("document.fonts.ready")
        page.evaluate("window.imageReady || Promise.resolve()")
        if not page.evaluate("typeof window.seek === 'function'"):
            page.close()
            raise MediaError("scene did not define window.seek(t)")
        return page

    def render(
        self,
        scene: dict[str, Any],
        style: Style,
        duration: float,
        out: Path,
        workdir: Path,
        html_file: Path | None = None,
    ) -> None:
        """Render a silent MP4 of exactly round(duration * fps) frames."""
        fps = self.fmt.fps
        frames = max(1, round(duration * fps))
        page = self._open(scene["type"], scene, style, duration, html_file, workdir)
        cmd = [
            require_tool("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error",
            "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
            *VIDEO_ARGS, "-r", str(fps), "-movflags", "+faststart", str(out),
        ]  # fmt: skip
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        assert ff.stdin is not None
        try:
            for i in range(frames):
                page.evaluate("t => window.seek(t)", i / fps)
                ff.stdin.write(page.screenshot(type="png"))
            ff.stdin.close()
            err = ff.stderr.read().decode() if ff.stderr else ""
            if ff.wait() != 0:
                raise MediaError(f"ffmpeg failed while encoding {out.name}:\n{err[-600:]}")
        except BaseException:
            ff.kill()
            raise
        finally:
            page.close()

    def still(
        self,
        scene: dict[str, Any],
        style: Style,
        duration: float,
        t: float,
        out: Path,
        workdir: Path,
        html_file: Path | None = None,
    ) -> None:
        """One PNG at time t, for quick visual review."""
        page = self._open(scene["type"], scene, style, duration, html_file, workdir)
        try:
            page.evaluate("t => window.seek(t)", t)
            out.write_bytes(page.screenshot(type="png"))
        finally:
            page.close()


def scene_html_path(scene: HtmlScene, storyboard_path: Path) -> Path:
    from .storyboard import resolve_path

    path = resolve_path(storyboard_path, scene.src)
    if not path.is_file():
        raise MediaError(f"html scene not found: {path}")
    return path
