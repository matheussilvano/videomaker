import pytest

from videomaker.storyboard import StoryboardError, load_storyboard

MIN = {"scenes": [{"type": "title", "text": "Hello"}]}


def test_minimal_storyboard_gets_defaults_and_ids(storyboard_file):
    sb = load_storyboard(storyboard_file(MIN))
    assert (sb.format.width, sb.format.height, sb.format.fps) == (1080, 1920, 30)
    assert sb.scenes[0].id == "s01-title"
    assert sb.captions.enabled and sb.voice.engine == "kokoro"


def test_format_presets(storyboard_file):
    sb = load_storyboard(storyboard_file({**MIN, "format": "landscape"}))
    assert (sb.format.width, sb.format.height) == (1920, 1080)


def test_unknown_preset_is_rejected(storyboard_file):
    with pytest.raises(StoryboardError, match="unknown format preset"):
        load_storyboard(storyboard_file({**MIN, "format": "cinema"}))


def test_odd_dimensions_are_rejected(storyboard_file):
    with pytest.raises(StoryboardError, match="even"):
        load_storyboard(storyboard_file({**MIN, "format": {"width": 1081, "height": 1920}}))


def test_unknown_field_is_rejected_with_its_path(storyboard_file):
    bad = {"scenes": [{"type": "title", "text": "x", "colour": "red"}]}
    with pytest.raises(StoryboardError, match=r"scenes\.0\.title\.colour"):
        load_storyboard(storyboard_file(bad))


def test_duplicate_ids_are_rejected(storyboard_file):
    scenes = [{"id": "a", "type": "title", "text": "1"}, {"id": "a", "type": "title", "text": "2"}]
    with pytest.raises(StoryboardError, match="duplicate scene id"):
        load_storyboard(storyboard_file({"scenes": scenes}))


def test_html_scene_requires_duration(storyboard_file):
    with pytest.raises(StoryboardError, match="duration"):
        load_storyboard(storyboard_file({"scenes": [{"type": "html", "src": "a.html"}]}))


def test_media_end_must_follow_start(storyboard_file):
    scene = {"type": "media", "src": "a.mp4", "start": 5, "end": 2}
    with pytest.raises(StoryboardError, match="end must be greater"):
        load_storyboard(storyboard_file({"scenes": [scene]}))


def test_story_scene_with_panel_and_card(storyboard_file):
    scene = {
        "type": "story",
        "pose": "point",
        "card": {"src": "p.jpg"},
        "panel": {"title": "T", "rows": [{"text": "A", "flag": "pt"}], "big": "(48) 1"},
    }
    sb = load_storyboard(storyboard_file({"scenes": [scene], "hud": {"badge": "1", "title": "X"}}))
    assert sb.hud is not None and sb.scenes[0].type == "story"


def test_invalid_json_and_missing_file(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{nope")
    with pytest.raises(StoryboardError, match="invalid JSON"):
        load_storyboard(bad)
    with pytest.raises(StoryboardError, match="not found"):
        load_storyboard(tmp_path / "missing.json")
