"""Storyboard model: the single JSON file that describes a whole video.

A storyboard is a list of scenes plus global format, style, voice and music.
Everything else (narration, rendering, captions, assembly) is derived from it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError, model_validator

FORMAT_PRESETS: dict[str, tuple[int, int]] = {
    "vertical": (1080, 1920),
    "landscape": (1920, 1080),
    "square": (1080, 1080),
}


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Format(_Strict):
    width: int = Field(default=1080, ge=64, le=7680)
    height: int = Field(default=1920, ge=64, le=7680)
    fps: int = Field(default=30, ge=1, le=120)

    @model_validator(mode="after")
    def _even(self) -> Format:
        if self.width % 2 or self.height % 2:
            raise ValueError("width and height must be even (H.264 requirement)")
        return self


class Style(_Strict):
    background: str = "#0b0b12"
    background_to: str | None = "#1b1033"
    foreground: str = "#f5f5f7"
    muted: str = "#a1a1b5"
    accent: str = "#7c5cff"
    font: str = "Inter, 'Helvetica Neue', 'DejaVu Sans', 'Liberation Sans', system-ui, sans-serif"


class Voice(_Strict):
    engine: Literal["kokoro", "none"] = "kokoro"
    name: str | None = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class Music(_Strict):
    path: str
    volume: float = Field(default=0.12, ge=0.0, le=1.0)
    duck: bool = True


class Captions(_Strict):
    enabled: bool = True
    words_per_cue: int = Field(default=4, ge=1, le=12)
    uppercase: bool = False
    # "impact": huge Anton caps with a thick black outline (Reels/TikTok look)
    style: Literal["clean", "impact"] = "clean"


class Character(_Strict):
    """The cartoon host of `story` scenes. Defaults: warm skin, short dark hair, white vestments."""

    skin: str = "#dba77a"
    hair: str = "#231814"
    robe: str = "#f6f1e6"
    trim: str = "#d6a636"
    collar: bool = True  # black clerical collar with the white tab


class Hud(_Strict):
    """Top info bar shown on every `story` scene (like a sports-card header)."""

    badge: str
    title: str
    subtitle: str | None = None
    right_top: str | None = None
    right_bottom: str | None = None


class _Scene(_Strict):
    id: str | None = None
    narration: str | None = None
    caption_text: str | None = (
        None  # shown instead of the narration (e.g. digits for a phone number)
    )
    duration: float | None = Field(default=None, gt=0, le=600)
    hold: float = Field(default=0.4, ge=0, le=5)


class TitleScene(_Scene):
    type: Literal["title"]
    text: str
    subtitle: str | None = None


class BulletsScene(_Scene):
    type: Literal["bullets"]
    title: str | None = None
    items: list[str] = Field(min_length=1, max_length=8)


class StatScene(_Scene):
    type: Literal["stat"]
    value: str
    label: str


class QuoteScene(_Scene):
    type: Literal["quote"]
    text: str
    author: str | None = None


class PhotoScene(_Scene):
    """A still photo with a slow camera move and an optional lower-third."""

    type: Literal["photo"]
    src: str
    title: str | None = None
    subtitle: str | None = None
    motion: Literal["zoom-in", "zoom-out", "pan-left", "pan-right"] = "zoom-in"
    focus: str = "50% 50%"  # CSS object-position, e.g. "50% 20%" to keep a face in frame
    fit: Literal["cover", "card"] = "cover"  # "card": sharp rounded photo on a blurred copy
    credit: str | None = None


class ContactScene(_Scene):
    """Closing call to action: headline, a name and a phone/WhatsApp number."""

    type: Literal["contact"]
    headline: str
    name: str | None = None
    phone: str
    note: str | None = None


class Card(_Strict):
    src: str
    focus: str = "50% 50%"
    credit: str | None = None


class PanelRow(_Strict):
    text: str
    value: str | None = None
    flag: Literal["de", "be", "pt"] | None = None


class Panel(_Strict):
    """An info card: title, optional rows with flags and one big line (e.g. a phone number)."""

    title: str
    subtitle: str | None = None
    rows: list[PanelRow] = Field(default_factory=list, max_length=6)
    big: str | None = None


class StoryScene(_Scene):
    """Flat-illustration scene: the cartoon host, a flat backdrop, and a photo card or info panel."""

    type: Literal["story"]
    backdrop: Literal["navy", "germany", "belgium", "portugal", "gold"] = "navy"
    pose: Literal["idle", "point", "wave", "cheer"] = "idle"
    side: Literal["left", "right", "center"] = "right"
    headline: str | None = None
    headline_sub: str | None = None
    card: Card | None = None
    panel: Panel | None = None
    chip: str | None = None
    place: str | None = None


class MediaScene(_Scene):
    """A video or image you already have (raw footage, a clip edited with video-use)."""

    type: Literal["media"]
    src: str
    start: float = Field(default=0.0, ge=0)
    end: float | None = Field(default=None, gt=0)
    fit: Literal["cover", "contain"] = "cover"
    audio: Literal["keep", "mute"] = "keep"
    caption: str | None = None

    @model_validator(mode="after")
    def _range(self) -> MediaScene:
        if self.end is not None and self.end <= self.start:
            raise ValueError("end must be greater than start")
        return self


class HtmlScene(_Scene):
    """A custom scene: your own HTML exposing window.seek(t) (see docs/scenes.md)."""

    type: Literal["html"]
    src: str
    duration: float = Field(gt=0, le=600)


Scene = Annotated[
    TitleScene
    | BulletsScene
    | StatScene
    | QuoteScene
    | PhotoScene
    | StoryScene
    | ContactScene
    | MediaScene
    | HtmlScene,
    Field(discriminator="type"),
]


class Storyboard(_Strict):
    title: str = "Untitled"
    language: str = "en"
    format: Format = Field(default_factory=lambda: Format())
    style: Style = Field(default_factory=lambda: Style())
    voice: Voice = Field(default_factory=lambda: Voice())
    music: Music | None = None
    captions: Captions = Field(default_factory=lambda: Captions())
    character: Character = Field(default_factory=lambda: Character())
    hud: Hud | None = None
    scenes: list[Scene] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def _expand_format_preset(cls, data: Any) -> Any:
        if isinstance(data, dict) and isinstance(data.get("format"), str):
            name = data["format"]
            if name not in FORMAT_PRESETS:
                raise ValueError(
                    f"unknown format preset {name!r}; use one of {sorted(FORMAT_PRESETS)}"
                )
            width, height = FORMAT_PRESETS[name]
            data = {**data, "format": {"width": width, "height": height}}
        return data

    @model_validator(mode="after")
    def _unique_ids(self) -> Storyboard:
        seen: set[str] = set()
        for i, scene in enumerate(self.scenes):
            scene.id = scene.id or f"s{i + 1:02d}-{scene.type}"
            if scene.id in seen:
                raise ValueError(f"duplicate scene id {scene.id!r}")
            seen.add(scene.id)
        return self


class StoryboardError(ValueError):
    """Raised with a readable message when a storyboard file is invalid."""


def load_storyboard(path: Path) -> Storyboard:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StoryboardError(f"storyboard not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StoryboardError(f"{path}: invalid JSON ({exc})") from exc
    try:
        return TypeAdapter(Storyboard).validate_python(raw)
    except ValidationError as exc:
        lines = []
        for err in exc.errors():
            where = ".".join(str(p) for p in err["loc"]) or "<root>"
            lines.append(f"  {where}: {err['msg']}")
        raise StoryboardError(f"{path} is not a valid storyboard:\n" + "\n".join(lines)) from exc


def resolve_path(storyboard_path: Path, ref: str) -> Path:
    """Paths inside a storyboard are relative to the storyboard file."""
    p = Path(ref).expanduser()
    return p if p.is_absolute() else (storyboard_path.parent / p).resolve()
