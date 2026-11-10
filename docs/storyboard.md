# Storyboard

One JSON file describes the whole video. Paths are relative to the file. Unknown fields are errors (with their path), so typos never silently do nothing.

```json
{
  "title": "My video",
  "language": "pt-br",
  "format": "vertical",
  "voice": { "engine": "kokoro", "name": "pm_alex", "speed": 0.95 },
  "captions": { "style": "impact", "words_per_cue": 3 },
  "hud": { "badge": "2027", "title": "TRIP", "subtitle": "THREE COUNTRIES", "right_top": "JUN" },
  "scenes": [ { "id": "intro", "type": "story", "pose": "wave", "headline": "Hello", "narration": "Hello!" } ]
}
```

## Top level
| Field | Notes |
| --- | --- |
| `format` | `vertical` 1080x1920, `landscape` 1920x1080, `square` 1080x1080, or `{width, height, fps}` (even sizes) |
| `language` | picks the narration language and default voice (`en pt es fr it hi ja zh`) |
| `voice` | `engine` `kokoro` or `none` (silent, durations from `duration`), `name` (`videomaker voices`), `speed` 0.5-2 |
| `music` | `{path, volume, duck}`: looped, ducked under speech, whole mix normalized to -14 LUFS |
| `captions` | `style` `clean` or `impact`, `words_per_cue`, `uppercase`, `enabled` |
| `character` | colors of the cartoon host: `skin hair robe trim collar` |
| `hud` | header bar on `story` scenes: `badge title subtitle right_top right_bottom` |
| `style` | colors/font for the non-story scenes |

## Every scene
`id` (auto: `s01-title`), `narration`, `caption_text` (shown instead of the narration: write numbers as digits here and as words in `narration`), `duration`, `hold` (seconds kept after speech, default 0.4).

**Timing rule:** narration is never cut. A scene lasts `max(duration, speech + hold)`. Without narration it lasts `duration`, or a reading-time default.

## Scene types
- **`story`**: flat-illustration scene with the cartoon host. `backdrop` (`navy germany belgium portugal gold`), `pose` (`idle point wave cheer`), `side` (`left right center`), `headline` + `headline_sub`, `card` (`src focus credit`: a photo in a frame), `panel` (`title subtitle rows[{text value flag}] big`), `chip` (tilted tag, e.g. a date), `place` (pill). The mouth follows the narration loudness.
- **`title`**, **`bullets`**, **`stat`** (counts up), **`quote`**: text scenes.
- **`photo`**: full-frame photo with a slow move and a lower-third. `fit: "card"` for small photos.
- **`contact`**: closing call to action with a phone/WhatsApp number.
- **`media`**: your video or image: `start end fit audio caption`. Narration over footage ducks the footage audio.
- **`html`**: your own page, see [scenes.md](scenes.md).

## Commands
```bash
videomaker validate storyboard.json     # plan + durations
videomaker still storyboard.json hook -t 2.5   # PNG of one scene
videomaker build storyboard.json -o out        # out/final.mp4, captions.srt, storyboard.resolved.json
videomaker build storyboard.json --scene hook  # only these scenes (debug)
```
Scenes are cached by content; unchanged scenes are not re-rendered. `--force` ignores the cache.
