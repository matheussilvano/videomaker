---
name: storyboard
description: Reference for videomaker's storyboard.json (scene types, story scenes with the cartoon host, HUD, captions styles, music, formats). Use when writing or fixing a storyboard.
---

# Storyboard reference

Full guide with examples: `docs/storyboard.md` in the videomaker repo. Validate with `videomaker validate`; unknown fields are errors with their path.

Top level: `title`, `language` (`en`, `pt-br`, `es`, ...), `format` (`vertical` | `landscape` | `square` | `{width,height,fps}`, even sizes), `style`, `voice` (`engine` `kokoro`|`none`, `name`, `speed`), `music` (`path`, `volume`, `duck`), `captions` (`enabled`, `style` `clean`|`impact`, `words_per_cue`, `uppercase`), `character` (`skin`, `hair`, `robe`, `trim`, `collar`), `hud` (`badge`, `title`, `subtitle`, `right_top`, `right_bottom`), `scenes`.

Every scene: `id`, `narration`, `caption_text` (shown instead of the narration), `duration`, `hold` (seconds after speech, default 0.4). Narration is never cut: a scene lasts at least speech + hold.

Scene types:
- `title`: `text`, `subtitle`
- `bullets`: `title`, `items` (1-8)
- `stat`: `value` (counts up if numeric), `label`
- `quote`: `text`, `author`
- `photo`: `src`, `title`, `subtitle`, `motion` (`zoom-in|zoom-out|pan-left|pan-right`), `focus`, `fit` (`cover|card`), `credit`
- `story`: cartoon host with `backdrop` (`navy|germany|belgium|portugal|gold`), `pose` (`idle|point|wave|cheer`), `side` (`left|right|center`), `headline`, `headline_sub`, `card` (`src`, `focus`, `credit`), `panel` (`title`, `subtitle`, `rows[{text,value,flag de|be|pt}]`, `big`), `chip`, `place`
- `contact`: `headline`, `name`, `phone`, `note`
- `media`: `src`, `start`, `end`, `fit`, `audio` (`keep|mute`), `caption`
- `html`: `src`, `duration` (your page defines `window.seek(t)`; globals `SCENE`, `STYLE`, `DURATION`, `FPS`)

Paths are relative to the storyboard file. Spell numbers in `narration`, digits in `caption_text`.
