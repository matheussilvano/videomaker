"""Turn a storyboard into final.mp4.

Per scene: narration -> duration -> render/trim -> one cached segment with audio.
Then: lossless concat -> music (ducked) + loudness -> captions burned last.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import wave
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import numpy as np

from . import __version__
from .captions import Cue, cues_for_text, write_ass, write_srt
from .media import (
    AUDIO_ARGS,
    VIDEO_ARGS,
    MediaError,
    duration_of,
    has_audio,
    is_image,
    run_ffmpeg,
)
from .render import Renderer, scene_html_path, template_version
from .storyboard import (
    BulletsScene,
    HtmlScene,
    MediaScene,
    PhotoScene,
    QuoteScene,
    Storyboard,
    StoryScene,
    load_storyboard,
    resolve_path,
)
from .tts import KokoroNarrator

Log = Callable[[str], None]
WORDS_PER_SECOND = 2.4  # used only when there is a narration but no audio to measure


class Narrator(Protocol):
    def synthesize(
        self, text: str, out: Path, *, language: str, voice: str | None, speed: float
    ) -> float: ...


@dataclass
class Segment:
    id: str
    path: Path
    start: float
    duration: float
    narration: str | None
    caption: str | None
    audible: bool = False


def default_duration(scene: Any) -> float:
    """Reading-time default when a scene has neither narration nor an explicit duration."""
    if isinstance(scene, BulletsScene):
        return 1.0 + 1.2 * len(scene.items)
    if isinstance(scene, QuoteScene):
        return 2.0 + 0.4 * len(scene.text.split())
    return 3.0


def resolve_duration(scene: Any, audio_len: float | None) -> float:
    """Narration is never cut: the scene lasts at least as long as the speech plus `hold`."""
    explicit = getattr(scene, "duration", None)
    if audio_len is not None:
        return float(max(explicit or 0.0, audio_len + scene.hold))
    if scene.narration:
        spoken = len(scene.narration.split()) / WORDS_PER_SECOND + scene.hold
        return float(max(explicit or 0.0, spoken))
    return float(explicit or default_duration(scene))


def mouth_envelope(wav_path: Path, fps: int) -> list[float]:
    """Narration loudness per video frame, 0..1: drives the cartoon host's mouth."""
    with wave.open(str(wav_path), "rb") as wf:
        rate = wf.getframerate()
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32)
    if data.size == 0:
        return []
    step = max(1, round(rate / fps))
    frames = data[: len(data) // step * step].reshape(-1, step)
    rms = np.sqrt((frames**2).mean(axis=1)) / 32768.0
    peak = float(np.percentile(rms, 95)) or 1.0
    return [round(float(v), 3) for v in np.clip(rms / peak, 0.0, 1.0)]


def _digest(*parts: object) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(json.dumps(part, sort_keys=True, default=str).encode())
    return h.hexdigest()[:16]


def _file_stamp(path: Path) -> list[object]:
    st = path.stat()
    return [str(path), st.st_size, int(st.st_mtime)]


def _media_segment(
    scene: MediaScene, src: Path, sb: Storyboard, duration: float, narration: Path | None, out: Path
) -> None:
    fmt = sb.format
    fit = (
        f"scale={fmt.width}:{fmt.height}:force_original_aspect_ratio=increase,"
        f"crop={fmt.width}:{fmt.height}"
        if scene.fit == "cover"
        else f"scale={fmt.width}:{fmt.height}:force_original_aspect_ratio=decrease,"
        f"pad={fmt.width}:{fmt.height}:(ow-iw)/2:(oh-ih)/2:color=black"
    )
    vf = f"{fit},setsar=1,fps={fmt.fps},tpad=stop_mode=clone:stop_duration=600,format=yuv420p"
    args: list[str | Path] = []
    if is_image(src):
        args += ["-loop", "1", "-framerate", str(fmt.fps), "-i", src]
        source_audio = False
    else:
        args += ["-ss", f"{scene.start}", "-i", src]
        source_audio = scene.audio == "keep" and has_audio(src)
    n = 1
    if narration:
        args += ["-i", narration]
        n += 1
    args += ["-f", "lavfi", "-t", f"{duration}", "-i", "anullsrc=r=48000:cl=stereo"]
    silence = n
    pad = f"aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{duration}"
    if narration and source_audio:
        af = (
            f"[0:a]volume=0.25,{pad}[a0];[1:a]{pad}[a1];"
            "[a0][a1]amix=inputs=2:duration=first:normalize=0[a]"
        )
    elif narration:
        af = f"[1:a]{pad}[a]"
    elif source_audio:
        af = f"[0:a]{pad}[a]"
    else:
        af = f"[{silence}:a]{pad}[a]"
    run_ffmpeg(
        [*args, "-filter_complex", f"[0:v]{vf}[v];{af}", "-map", "[v]", "-map", "[a]",
         "-t", f"{duration}", *VIDEO_ARGS, "-r", str(fmt.fps), *AUDIO_ARGS, out]
    )  # fmt: skip


def _mux_generated(video: Path, narration: Path | None, duration: float, out: Path) -> None:
    pad = f"aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{duration}"
    if narration:
        args: list[str | Path] = ["-i", video, "-i", narration, "-filter_complex", f"[1:a]{pad}[a]"]
    else:
        args = [
            "-i", video, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex", f"[1:a]{pad}[a]",
        ]  # fmt: skip
    run_ffmpeg([*args, "-map", "0:v", "-map", "[a]", "-c:v", "copy", *AUDIO_ARGS,
                "-t", f"{duration}", out])  # fmt: skip


def build(
    storyboard_path: Path,
    out_dir: Path,
    *,
    force: bool = False,
    only: set[str] | None = None,
    log: Log = print,
    narrator: Narrator | None = None,
) -> Path:
    """Render the whole storyboard. Unchanged scenes come from the cache."""
    sb_path = storyboard_path.resolve()
    sb = load_storyboard(sb_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    cache = out_dir / ".cache"
    cache.mkdir(exist_ok=True)
    tver = template_version()
    narrator = narrator or KokoroNarrator()
    segments: list[Segment] = []
    cursor = 0.0

    with Renderer(sb.format, _globals(sb)) as renderer:
        for scene in sb.scenes:
            sid = str(scene.id)
            if only and sid not in only:
                continue
            raw: dict[str, Any] = scene.model_dump()
            narration_wav: Path | None = None
            audio_len: float | None = None
            if scene.narration and sb.voice.engine == "kokoro":
                key = _digest(scene.narration, sb.language, sb.voice.model_dump())
                narration_wav = cache / f"{sid}-{key}.wav"
                meta = narration_wav.with_suffix(".txt")
                if force or not narration_wav.exists() or not meta.exists():
                    log(f"  narrating {sid}")
                    audio_len = narrator.synthesize(
                        scene.narration, narration_wav, language=sb.language,
                        voice=sb.voice.name, speed=sb.voice.speed,
                    )  # fmt: skip
                    meta.write_text(str(audio_len))
                else:
                    audio_len = float(meta.read_text())

            src: Path | None = None
            stamp: list[object] = []
            if isinstance(scene, StoryScene):
                if scene.card:
                    card_file = resolve_path(sb_path, scene.card.src)
                    if not card_file.is_file():
                        raise MediaError(f"scene {sid}: card photo not found: {card_file}")
                    raw["card"]["src_url"] = card_file.as_uri()
                    stamp = _file_stamp(card_file)
                raw["env"] = mouth_envelope(narration_wav, sb.format.fps) if narration_wav else []
            if isinstance(scene, MediaScene | PhotoScene | HtmlScene):
                src = resolve_path(sb_path, scene.src)
                if not src.is_file():
                    raise MediaError(f"scene {sid}: file not found: {src}")
                stamp = _file_stamp(src)
            if isinstance(scene, MediaScene) and scene.duration is None and audio_len is None:
                total = 3.0 if is_image(src or Path()) else duration_of(src or Path())
                scene_len = (scene.end if scene.end else total) - scene.start
                duration = resolve_duration(scene.model_copy(update={"duration": scene_len}), None)
            else:
                duration = resolve_duration(scene, audio_len)

            key = _digest(raw, sb.format.model_dump(), sb.style.model_dump(), duration, audio_len,
                          stamp, tver, __version__,
                          sb.hud.model_dump() if sb.hud else None,
                          sb.character.model_dump())  # fmt: skip
            seg = cache / f"{sid}-{key}.mp4"
            if force or not seg.exists():
                log(f"  rendering {sid} ({duration:.1f}s)")
                tmp = cache / f"{sid}-{key}.tmp.mp4"
                if isinstance(scene, MediaScene):
                    assert src is not None
                    _media_segment(scene, src, sb, duration, narration_wav, seg)
                else:
                    if isinstance(scene, PhotoScene):
                        raw["src_url"] = src.as_uri() if src else ""
                    renderer.render(
                        raw, sb.style, duration, tmp, out_dir,
                        html_file=scene_html_path(scene, sb_path) if isinstance(scene, HtmlScene) else None,
                    )  # fmt: skip
                    _mux_generated(tmp, narration_wav, duration, seg)
                    tmp.unlink(missing_ok=True)
            else:
                log(f"  cached    {sid}")
            caption = scene.caption_text or (
                scene.caption if isinstance(scene, MediaScene) else None
            )
            audible = narration_wav is not None or (
                isinstance(scene, MediaScene)
                and scene.audio == "keep"
                and src is not None
                and not is_image(src)
                and has_audio(src)
            )
            segments.append(Segment(sid, seg, cursor, duration, scene.narration, caption, audible))
            cursor += duration

    return _finish(sb, sb_path, out_dir, segments, log)


def _globals(sb: Storyboard) -> dict[str, Any]:
    return {"HUD": sb.hud.model_dump() if sb.hud else None, "CHARACTER": sb.character.model_dump()}


def _finish(
    sb: Storyboard, sb_path: Path, out_dir: Path, segments: list[Segment], log: Log
) -> Path:
    listing = out_dir / "segments.txt"
    listing.write_text("".join(f"file '{s.path.resolve()}'\n" for s in segments))
    joined = out_dir / ".joined.mp4"
    run_ffmpeg(["-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", joined])
    listing.unlink()

    mixed = out_dir / ".mixed.mp4"
    # loudnorm on pure silence yields NaN/Inf in recent ffmpeg builds: only touch audible mixes.
    audible = sb.music is not None or any(s.audible for s in segments)
    loud = "loudnorm=I=-14:TP=-1.5:LRA=11"
    if sb.music:
        music = resolve_path(sb_path, sb.music.path)
        if not music.is_file():
            raise MediaError(f"music file not found: {music}")
        vol = sb.music.volume
        graph = (
            f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol}[m];"
            + (
                "[0:a]asplit=2[v][sc];[m][sc]sidechaincompress=threshold=0.04:ratio=8:"
                "attack=20:release=400[md];[v][md]amix=inputs=2:duration=first:normalize=0[mix];"
                if sb.music.duck
                else "[0:a][m]amix=inputs=2:duration=first:normalize=0[mix];"
            )
            + f"[mix]{loud}[a]"
        )
        run_ffmpeg(["-i", joined, "-stream_loop", "-1", "-i", music, "-filter_complex", graph,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", *AUDIO_ARGS, "-shortest", mixed])  # fmt: skip
    elif audible:
        run_ffmpeg(["-i", joined, "-af", loud, "-c:v", "copy", *AUDIO_ARGS, mixed])
    else:
        shutil.copy(joined, mixed)
    joined.unlink()

    cues: list[Cue] = []
    for s in segments:
        text = s.caption or s.narration
        if text and sb.captions.enabled:
            span = max(0.1, s.duration - (0.4 if s.narration else 0.2))
            cues += cues_for_text(text, s.start, span, words_per_cue=sb.captions.words_per_cue,
                                  uppercase=sb.captions.uppercase or sb.captions.style == "impact")  # fmt: skip
    final = out_dir / "final.mp4"
    if cues:
        write_srt(cues, out_dir / "captions.srt")
        write_ass(
            cues,
            sb.format,
            sb.style,
            out_dir / "captions.ass",
            impact=sb.captions.style == "impact",
        )
        fonts = (Path(__file__).parent / "fonts").resolve()
        run_ffmpeg(["-i", mixed.name, "-vf", f"ass=captions.ass:fontsdir={fonts}", *VIDEO_ARGS, "-c:a", "copy",
                    "-movflags", "+faststart", final.name], cwd=out_dir)  # fmt: skip
        mixed.unlink()
    else:
        shutil.move(mixed, final)

    (out_dir / "storyboard.resolved.json").write_text(
        json.dumps(
            {
                "title": sb.title,
                "total_seconds": round(sum(s.duration for s in segments), 2),
                "scenes": [
                    {"id": s.id, "start": round(s.start, 2), "duration": round(s.duration, 2)}
                    for s in segments
                ],
            },
            indent=2,
        )  # fmt: skip
    )
    log(f"done: {final} ({sum(s.duration for s in segments):.1f}s)")
    return final


def still(storyboard_path: Path, out_dir: Path, scene_id: str, t: float, log: Log = print) -> Path:
    """One PNG of a scene at time t, to review a look before paying for a full render."""
    sb_path = storyboard_path.resolve()
    sb = load_storyboard(sb_path)
    scene = next((s for s in sb.scenes if s.id == scene_id), None)
    if scene is None:
        raise MediaError(f"no scene {scene_id!r}. Scenes: {[s.id for s in sb.scenes]}")
    if isinstance(scene, MediaScene):
        raise MediaError(
            "stills are for generated scenes (title, bullets, stat, quote, photo, contact, html)"
        )
    duration = resolve_duration(scene, None)
    raw: dict[str, Any] = scene.model_dump()
    html_file = None
    if isinstance(scene, PhotoScene):
        raw["src_url"] = resolve_path(sb_path, scene.src).as_uri()
    if isinstance(scene, StoryScene):
        if scene.card:
            raw["card"]["src_url"] = resolve_path(sb_path, scene.card.src).as_uri()
        raw["env"] = []
    if isinstance(scene, HtmlScene):
        html_file = scene_html_path(scene, sb_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"still-{scene_id}-{t:.1f}.png"
    with Renderer(sb.format, _globals(sb)) as r:
        r.still(raw, sb.style, duration, min(t, duration), out, out_dir, html_file)
    log(f"wrote {out}")
    return out
