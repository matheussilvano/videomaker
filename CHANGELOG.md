# Changelog

## Unreleased
- `character.svg`: bring your own host drawing, animated through `vm-*` ids (arms, eyes, mouth).
- `story` scenes: `shot: "close"` pushes the camera in on the host's face.
- Captions: `*word*` highlights words in the accent color.
- Skip loudnorm on silent mixes (it produced NaN in recent ffmpeg).

## 0.1.0
- First release: storyboard JSON to `final.mp4` (`videomaker build`), cached per scene.
- Scene types: `title`, `bullets`, `stat`, `quote`, `photo`, `contact`, `story` (cartoon host with a lip-synced mouth, photo cards, info panels, HUD), `media` (footage and images), `html` (custom `window.seek(t)` pages).
- Free local narration with Kokoro (English, Portuguese, Spanish, French, Italian, Hindi, Japanese, Chinese), voices and models checksum-pinned.
- Captions: `clean` and `impact` (Reels look), SRT and ASS export, burned last.
- Music with ducking and loudness normalization (-14 LUFS).
- `videomaker setup` installs models, a browser and the pinned video-use and motion-design skills; `doctor`, `validate`, `still`, `voices`, `transcribe` (local Whisper in video-use's JSON shape).
- Claude Code plugin with `make`, `footage`, `storyboard` and `setup` skills.
