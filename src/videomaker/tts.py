"""Local, free narration with Kokoro (ONNX). Runs offline after `videomaker setup --models`."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from .media import MediaError

# language prefix -> (kokoro lang code, default voice)
LANGUAGES: dict[str, tuple[str, str]] = {
    "en": ("en-us", "af_heart"),
    "pt": ("pt-br", "pf_dora"),
    "es": ("es", "ef_dora"),
    "fr": ("fr-fr", "ff_siwis"),
    "it": ("it", "if_sara"),
    "hi": ("hi", "hf_alpha"),
    "ja": ("ja", "jf_alpha"),
    "zh": ("cmn", "zf_xiaobei"),
}

_BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
MODEL_FILES = {
    "kokoro-v1.0.int8.onnx": (
        _BASE + "kokoro-v1.0.int8.onnx",
        "6e742170d309016e5891a994e1ce1559c702a2ccd0075e67ef7157974f6406cb",
    ),
    "voices-v1.0.bin": (
        _BASE + "voices-v1.0.bin",
        "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
    ),
}


def home_dir() -> Path:
    return Path(os.environ.get("VIDEOMAKER_HOME", "~/.cache/videomaker")).expanduser()


def models_dir() -> Path:
    return home_dir() / "models"


def models_ready() -> bool:
    return all((models_dir() / name).is_file() for name in MODEL_FILES)


def language_defaults(language: str) -> tuple[str, str]:
    prefix = language.lower().split("-")[0]
    if prefix not in LANGUAGES:
        raise MediaError(
            f"No narration voice for language {language!r}. Supported: {sorted(LANGUAGES)}"
        )
    return LANGUAGES[prefix]


class KokoroNarrator:
    """Loads the model once and writes one WAV per narration."""

    def __init__(self) -> None:
        self._kokoro: Any = None

    def _load(self) -> Any:
        if self._kokoro is None:
            if not models_ready():
                raise MediaError(
                    "Narration models are missing. Run `videomaker setup --models` (about 120 MB)."
                )
            from kokoro_onnx import Kokoro

            self._kokoro = Kokoro(
                str(models_dir() / "kokoro-v1.0.int8.onnx"), str(models_dir() / "voices-v1.0.bin")
            )
        return self._kokoro

    def voices(self) -> list[str]:
        return sorted(self._load().get_voices())

    def synthesize(
        self, text: str, out: Path, *, language: str, voice: str | None, speed: float
    ) -> float:
        """Write a mono WAV and return its duration in seconds."""
        lang_code, default_voice = language_defaults(language)
        samples, rate = self._load().create(
            text, voice=voice or default_voice, speed=speed, lang=lang_code
        )
        audio = np.asarray(samples, dtype=np.float32)
        sf.write(str(out), audio, rate, subtype="PCM_16")
        return float(len(audio) / rate)
