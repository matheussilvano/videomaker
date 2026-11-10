"""Burned-in captions. Timing is proportional to word length inside each narration."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .storyboard import Format, Style


@dataclass(frozen=True)
class Cue:
    start: float
    end: float
    text: str


def _parse_highlights(text: str) -> list[tuple[str, bool]]:
    """Split text into (word, highlighted). `*04 JUN*` highlights both words.

    Every `*` toggles the highlight, wherever it sits in a token, so `*Fátima*,` works.
    """
    out: list[tuple[str, bool]] = []
    on = False
    for token in text.split():
        chars: list[str] = []
        hl = False
        for ch in token:
            if ch == "*":
                on = not on
                continue
            chars.append(ch)
            hl = hl or on
        if chars:
            out.append(("".join(chars), hl))
    return out


def cues_for_text(
    text: str, start: float, duration: float, *, words_per_cue: int = 4, uppercase: bool = False
) -> list[Cue]:
    """Split text into short cues spread over [start, start + duration] by character weight.

    `*word*` marks highlighted words; they come out as `*word*` in the cue text.
    """
    words = _parse_highlights(text)
    if not words or duration <= 0:
        return []
    weights = [len(w) + 1 for w, _ in words]
    total = float(sum(weights))
    cues: list[Cue] = []
    cursor = start
    for i in range(0, len(words), words_per_cue):
        chunk = words[i : i + words_per_cue]
        span = duration * sum(weights[i : i + words_per_cue]) / total
        parts = [(w.upper() if uppercase else w, hl) for w, hl in chunk]
        label = " ".join(f"*{w}*" if hl else w for w, hl in parts)
        cues.append(Cue(cursor, cursor + span, label))
        cursor += span
    return cues


def _split(ms: int) -> tuple[int, int, int, int]:
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return h, m, s, ms


def write_srt(cues: list[Cue], path: Path) -> None:
    def stamp(seconds: float) -> str:
        h, m, s, ms = _split(round(seconds * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    blocks = [
        f"{i}\n{stamp(c.start)} --> {stamp(c.end)}\n{c.text.replace('*', '')}\n"
        for i, c in enumerate(cues, 1)
    ]
    path.write_text("\n".join(blocks), encoding="utf-8")


def _ass_time(seconds: float) -> str:
    h, m, s, ms = _split(round(seconds * 1000))
    return f"{h}:{m:02d}:{s:02d}.{ms // 10:02d}"


def write_ass(
    cues: list[Cue], fmt: Format, style: Style, path: Path, *, impact: bool = False
) -> None:
    """ASS file in the video's own resolution, so font sizes are real pixels."""
    size = round(min(fmt.width, fmt.height) * (0.092 if impact else 0.065))
    margin_v = round(fmt.height * (0.085 if impact else 0.07))
    margin_h = round(fmt.width * 0.08)
    font = "Anton" if impact else (style.font.split(",")[0].strip().strip("'\"") or "DejaVu Sans")
    outline = max(4, size // 7) if impact else max(2, size // 14)
    bold = 0 if impact else 1  # Anton is already heavy; synthetic bold would smear it
    rgb = style.accent.lstrip("#")
    hl = "&H" + (rgb[4:6] + rgb[2:4] + rgb[0:2]).upper() if len(rgb) == 6 else "&H00D7FF"
    head = (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {fmt.width}\nPlayResY: {fmt.height}\nWrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,"
        f"{bold},0,0,0,100,100,1,0,1,{outline},0,2,{margin_h},{margin_h},{margin_v},1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    lines = []
    for c in cues:
        text = c.text.replace("\n", " ").replace("{", "(").replace("}", ")")
        text = re.sub(r"\*([^*]+)\*", lambda m: f"{{\\c{hl}&}}{m.group(1)}{{\\c&HFFFFFF&}}", text)
        lines.append(f"Dialogue: 0,{_ass_time(c.start)},{_ass_time(c.end)},Default,,0,0,0,,{text}")
    path.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
