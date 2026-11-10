"""videomaker command line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .media import MediaError
from .storyboard import StoryboardError


def _build(args: argparse.Namespace) -> int:
    from .assemble import build

    only = set(args.scene) if args.scene else None
    build(args.storyboard, args.out, force=args.force, only=only)
    return 0


def _still(args: argparse.Namespace) -> int:
    from .assemble import still

    still(args.storyboard, args.out, args.scene, args.t)
    return 0


def _validate(args: argparse.Namespace) -> int:
    from .assemble import resolve_duration
    from .storyboard import load_storyboard

    sb = load_storyboard(args.storyboard)
    total = 0.0
    for s in sb.scenes:
        d = resolve_duration(s, None)
        total += d
        print(f"{s.id:<22} {s.type:<8} ~{d:4.1f}s" + ("  (narrated)" if s.narration else ""))
    print(f"\n{len(sb.scenes)} scenes, ~{total:.0f}s before narration is measured")
    return 0


def _doctor(_: argparse.Namespace) -> int:
    from .doctor import report, run_checks

    return report(run_checks())


def _setup(args: argparse.Namespace) -> int:
    from . import install

    everything = not (args.models or args.browser or args.skills)
    if args.models or everything:
        install.install_models()
    if args.browser or everything:
        install.install_browser()
    if args.skills or everything:
        install.install_skills()
    return 0


def _voices(_: argparse.Namespace) -> int:
    from .tts import KokoroNarrator

    print("\n".join(KokoroNarrator().voices()))
    return 0


def _transcribe(args: argparse.Namespace) -> int:
    from .transcribe import transcribe

    video = args.video.resolve()
    transcribe(video, args.edit_dir or video.parent / "edit", language=args.language,
               model=args.model, audio_track=args.audio_track)  # fmt: skip
    return 0


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="videomaker", description="Make videos end to end.")
    p.add_argument("--version", action="version", version=f"videomaker {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="render a storyboard to out/final.mp4")
    b.add_argument("storyboard", type=Path)
    b.add_argument("-o", "--out", type=Path, default=Path("out"))
    b.add_argument("--scene", action="append", help="only these scene ids (repeatable)")
    b.add_argument("--force", action="store_true", help="ignore the cache")
    b.set_defaults(func=_build)

    s = sub.add_parser("still", help="PNG of one scene at time t, for a quick look")
    s.add_argument("storyboard", type=Path)
    s.add_argument("scene")
    s.add_argument("-t", type=float, default=1.5)
    s.add_argument("-o", "--out", type=Path, default=Path("out"))
    s.set_defaults(func=_still)

    v = sub.add_parser("validate", help="check a storyboard and print the scene plan")
    v.add_argument("storyboard", type=Path)
    v.set_defaults(func=_validate)

    sub.add_parser("doctor", help="check ffmpeg, browser, models, skills").set_defaults(
        func=_doctor
    )

    st = sub.add_parser("setup", help="install models, browser and upstream skills")
    st.add_argument("--models", action="store_true", help="narration voices (~120 MB)")
    st.add_argument("--browser", action="store_true", help="Playwright Chromium")
    st.add_argument("--skills", action="store_true", help="video-use + motion-design, pinned")
    st.set_defaults(func=_setup)

    sub.add_parser("voices", help="list narration voices").set_defaults(func=_voices)

    t = sub.add_parser("transcribe", help="free local transcript in video-use's format")
    t.add_argument("video", type=Path)
    t.add_argument("--edit-dir", type=Path)
    t.add_argument("--language")
    t.add_argument("--model", default="medium")
    t.add_argument("--audio-track", type=int, default=0)
    t.set_defaults(func=_transcribe)
    return p


def main(argv: list[str] | None = None) -> None:
    args = make_parser().parse_args(argv)
    try:
        sys.exit(args.func(args))
    except (StoryboardError, MediaError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
