---
name: make
description: Make a finished video from an idea, a script/PDF, photos or raw footage. Plans a storyboard, narrates it with a free local voice, renders animated scenes (cartoon host, photo cards, info panels, captions), edits footage and exports final.mp4. Use for "make a video / ad / reel / explainer", "turn this script into a video", "animate this".
---

# Make a video

Answer in the user's language. Run `videomaker doctor` first; if `videomaker` is missing or a required check fails, use the `setup` skill. Work in a project folder (`~/videos/<name>/`), not inside a code repo.

## 1. Intake (one round, only what is missing)
Goal and audience, format (default **vertical 1080x1920**; `landscape`, `square`), language, target length (Reels/Shorts: 30-60 s), tone, the call to action (who to contact, how), and which assets exist (photos, footage, logo, music, a script or PDF). Read any PDF/script yourself (`pdftotext -layout`) and take facts only from it.

## 2. Facts and honesty
- Never invent prices, dates, numbers, testimonials or availability. Use what the user or their documents say; if the user states a claim ("few spots left"), use their wording.
- A person's photo, phone number or name goes in the video only if the user supplied it for this video. Keep such projects out of public repos.
- Illustrative data must be labelled as such on screen.

## 3. Assets
- User photos first. Otherwise free images from Wikimedia Commons (CC0, public domain, CC BY, CC BY-SA only), downloaded at a sensible width, **looked at before use** (filenames lie), with the credit on screen via `card.credit` / `credit`.
- Low-resolution photos (<1000 px) belong in a `story` card or a photo `fit: "card"`, never full-bleed.
- Music: only a file the user provides or a clearly licensed one; credit it.

## 4. Storyboard
Write `storyboard.json` (schema and scene types: `storyboard` skill, `docs/storyboard.md`).
- Hook in the first 2 seconds; one idea per scene; 2-6 s per scene; call to action last.
- Narration is short, spoken language. **Spell numbers and phone digits out in `narration`** and put the digits in `caption_text`.
- Reels look: `"captions": {"style": "impact"}`, a `hud` header, `story` scenes with the cartoon host pointing at a photo card or info panel, a date `chip` and a `place` pill.

## 5. Route each scene
| Material | Use |
| --- | --- |
| Text, stats, quotes, lists | `title`, `stat`, `quote`, `bullets` |
| Cartoon host + photo or info card | `story` |
| One photo with a camera move | `photo` |
| Raw footage to clean up (cuts, fillers, grade) | `footage` skill, then a `media` scene |
| Anything bespoke | `html` scene (`window.seek(t)`), or the `motion-design` skill if installed |

## 6. Check before the full render
1. `videomaker validate storyboard.json` (plan and ~durations).
2. `videomaker still storyboard.json <scene> -t 2.5` for two or three different scenes; **open the PNGs** and fix overlaps, cropped text or wrong photos.
3. `videomaker build storyboard.json -o out` (cached: re-run after small edits; `--scene id` for one scene, `--force` to ignore the cache). Long renders: run in the background.

## 7. QA and delivery
Check `ffprobe` duration against `out/storyboard.resolved.json`; extract a frame at the start of a few scenes (`ffmpeg -ss T -i out/final.mp4 -frames:v 1 f.png`) and look at them, especially the captions and the last scene. Report: path of `out/final.mp4`, length, `out/captions.srt`, the photo credits to paste in the post caption, and anything not verified (for example how the voice sounds in the user's language).
