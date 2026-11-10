import wave
from pathlib import Path

import numpy as np

from videomaker.assemble import default_duration, mouth_envelope, resolve_duration
from videomaker.captions import cues_for_text, write_ass, write_srt
from videomaker.storyboard import Format, Style, load_storyboard


def scenes(storyboard_file, *scene):
    return load_storyboard(storyboard_file({"scenes": list(scene)})).scenes


def test_narration_is_never_cut_by_a_shorter_duration(storyboard_file):
    (s,) = scenes(storyboard_file, {"type": "title", "text": "x", "narration": "hi", "duration": 1})
    assert resolve_duration(s, audio_len=4.0) == 4.0 + s.hold


def test_explicit_duration_wins_when_longer_than_speech(storyboard_file):
    (s,) = scenes(storyboard_file, {"type": "title", "text": "x", "narration": "hi", "duration": 9})
    assert resolve_duration(s, audio_len=2.0) == 9


def test_default_durations(storyboard_file):
    t, b = scenes(
        storyboard_file,
        {"type": "title", "text": "x"},
        {"id": "b", "type": "bullets", "items": ["a", "b", "c"]},
    )
    assert default_duration(t) == 3.0
    assert resolve_duration(b, None) == 1.0 + 1.2 * 3


def test_unmeasured_narration_uses_word_count(storyboard_file):
    (s,) = scenes(
        storyboard_file, {"type": "title", "text": "x", "narration": "um dois tres quatro"}
    )
    assert resolve_duration(s, None) > 1.5


def test_cues_cover_the_whole_span_in_order():
    cues = cues_for_text("one two three four five six seven", 10.0, 7.0, words_per_cue=3)
    assert [c.text for c in cues] == ["one two three", "four five six", "seven"]
    assert cues[0].start == 10.0 and abs(cues[-1].end - 17.0) < 1e-9
    assert all(a.end <= b.start + 1e-9 for a, b in zip(cues, cues[1:], strict=False))


def test_cues_empty_input():
    assert cues_for_text("", 0, 5) == []
    assert cues_for_text("hi", 0, 0) == []


def test_srt_and_ass_output(tmp_path: Path):
    cues = cues_for_text("hello {world}", 0.0, 2.0)
    write_srt(cues, tmp_path / "a.srt")
    assert "00:00:00,000 --> 00:00:02,000" in (tmp_path / "a.srt").read_text()
    write_ass(cues, Format(), Style(), tmp_path / "a.ass", impact=True)
    ass = (tmp_path / "a.ass").read_text()
    assert "PlayResX: 1080" in ass and "Style: Default,Anton," in ass
    assert "{world}" not in ass  # braces would be parsed as ASS override tags


def test_mouth_envelope_follows_loudness(tmp_path: Path):
    rate = 16000
    t = np.arange(rate * 2) / rate
    audio = np.where(t < 1.0, 0.0, 0.5 * np.sin(2 * np.pi * 220 * t))
    path = tmp_path / "v.wav"
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    env = mouth_envelope(path, fps=30)
    assert len(env) == 60
    assert max(env[:25]) < 0.05 and min(env[35:]) > 0.5


def test_highlight_markers_survive_chunking_and_are_stripped_for_srt(tmp_path: Path):
    cues = cues_for_text("Dia *4 de junho* em *Fátima* hoje", 0.0, 6.0, words_per_cue=3)
    assert [c.text for c in cues] == ["Dia *4* *de*", "*junho* em *Fátima*", "hoje"]
    write_srt(cues, tmp_path / "a.srt")
    assert "*" not in (tmp_path / "a.srt").read_text()
    write_ass(cues, Format(), Style(accent="#f2c230"), tmp_path / "a.ass")
    ass = (tmp_path / "a.ass").read_text()
    assert r"{\c&H30C2F2&}4{\c&HFFFFFF&}" in ass  # accent #f2c230 in ASS BGR order


def test_cue_without_highlights_is_unchanged():
    assert cues_for_text("plain words here", 0, 3, words_per_cue=5)[0].text == "plain words here"


def test_highlight_followed_by_punctuation_leaves_no_stray_asterisks():
    cues = cues_for_text("Primeiro, o *embarque*, depois *Fátima*. Fim", 0.0, 5.0, words_per_cue=10)
    assert cues[0].text == "Primeiro, o *embarque,* depois *Fátima.* Fim"
    assert cues[0].text.count("*") % 2 == 0
