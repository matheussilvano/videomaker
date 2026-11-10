"""Free local transcription that writes the word-level JSON video-use expects.

video-use's own transcriber needs a paid ElevenLabs key. This writes the same
shape (type/text/start/end/speaker_id per word) with faster-whisper, so
`pack_transcripts.py` and the rest of video-use work unchanged.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from .media import MediaError, run_ffmpeg


def transcribe(
    video: Path, edit_dir: Path, *, language: str | None, model: str, audio_track: int = 0
) -> Path:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise MediaError("faster-whisper is not installed. Run: uv sync --extra asr") from None
    out = edit_dir / "transcripts" / f"{video.stem}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        print(f"cached: {out}")
        return out
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        run_ffmpeg(["-i", video, "-map", f"0:a:{audio_track}", "-vn", "-ac", "1", "-ar", "16000",
                    "-c:a", "pcm_s16le", wav])  # fmt: skip
        import wave

        with wave.open(str(wav), "rb") as wf:
            pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    audio = pcm.astype(np.float32) / 32768.0
    whisper = WhisperModel(model, device="auto", compute_type="int8")
    segments, info = whisper.transcribe(
        audio, language=language, word_timestamps=True, condition_on_previous_text=False,
        initial_prompt="Ééé, hum, tipo, né... Uh, um, like, you know, so...",
    )  # fmt: skip
    words: list[dict[str, Any]] = []
    prev: float | None = None
    for seg in segments:
        for w in seg.words or []:
            text = w.word.strip()
            if not text:
                continue
            if prev is not None and w.start > prev:
                words.append({"type": "spacing", "text": " ", "start": prev, "end": float(w.start),
                              "speaker_id": "speaker_0"})  # fmt: skip
            words.append({"type": "word", "text": text, "start": float(w.start), "end": float(w.end),
                          "speaker_id": "speaker_0"})  # fmt: skip
            prev = float(w.end)
    out.write_text(
        json.dumps({"language_code": language or info.language, "words": words}, indent=2)
    )
    print(f"saved: {out} ({sum(1 for w in words if w['type'] == 'word')} words)")
    return out
