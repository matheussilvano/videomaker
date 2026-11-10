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
| `character` | the cartoon host: colors `skin hair robe trim collar`, or your own drawing with `svg` (see [Custom character](#custom-character)) |
| `hud` | header bar on `story` scenes: `badge title subtitle right_top right_bottom` |
| `style` | colors/font for the non-story scenes |

## Every scene
`id` (auto: `s01-title`), `narration`, `caption_text` (shown instead of the narration: write numbers as digits here and as words in `narration`; wrap words in `*asterisks*` to highlight them in the accent color, e.g. `Dia *4* em *Fátima*`), `duration`, `hold` (seconds kept after speech, default 0.4).

**Timing rule:** narration is never cut. A scene lasts `max(duration, speech + hold)`. Without narration it lasts `duration`, or a reading-time default.

## Scene types
- **`story`**: flat-illustration scene with the cartoon host. `backdrop` (`navy germany belgium portugal gold`), `pose` (`idle point wave cheer`), `shot` (`wide` or `close`: the camera pushes in on the face), `side` (`left right center`), `headline` + `headline_sub`, `card` (`src focus credit`: a photo in a frame), `panel` (`title subtitle rows[{text value flag}] big`), `chip` (tilted tag, e.g. a date), `place` (pill). The mouth follows the narration loudness.
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

## Custom character

Point `character.svg` at your own SVG. Videomaker animates it through ids and `data-` attributes, all optional except the layout ones:

```xml
<svg viewBox="-60 -40 308 400"
     data-floor="316"      <!-- y of the ground line, in viewBox units -->
     data-cx="94"          <!-- x of the body centre -->
     data-body-h="291"     <!-- head-top to floor height; sets the on-screen size -->
     data-head="94 72"     <!-- face centre, used by the close shot -->
     data-mirror="auto">   <!-- flip when side is "right" so the raised arm points at the card -->
  <g id="vm-arm-l" data-pivot="56 120" data-state="down" data-raise="150">...</g>
  <g id="vm-arm-r" data-pivot="135 111" data-state="up"   data-lower="140">...</g>
  <g id="vm-eyes"  data-pivot="94 72">...</g>              <!-- blinks (scaleY) -->
  <g id="vm-mouth" data-pivot="94 95" data-open="0.6">...</g> <!-- grows with the narration loudness -->
</svg>
```
An arm drawn hanging down is `data-state="down"` with `data-raise` degrees to lift it (negative for an arm on the right); an arm drawn raised is `data-state="up"` with `data-lower` degrees to drop it. Make the viewBox larger than the drawing so raised arms are not clipped. Remove any background from the SVG: the scene draws the floor and wall.

Drawings of real people belong in your private project folder, not in a public repository.
