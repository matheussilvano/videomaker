---
name: footage
description: Edit raw footage (talking heads, takes, interviews) by cutting filler words and silences, grading and subtitling, then use the result inside a videomaker storyboard. Use when the user has video files to clean up before or inside a video.
---

# Edit raw footage

This skill delegates to the `video-use` skill (installed by `videomaker setup --skills`). Read its `SKILL.md` and `helpers/` first and follow its rules: confirm the cut strategy with the user before cutting, never cut inside a word, pad cut edges, subtitles last.

## Transcription without a paid key
video-use transcribes with ElevenLabs Scribe. If there is no `ELEVENLABS_API_KEY`, use the free local equivalent, which writes the same JSON shape:

```bash
videomaker transcribe path/to/take.mp4 --language pt   # needs the asr extra; first run downloads the model
```

Then continue with video-use's own `helpers/pack_transcripts.py --edit-dir <dir>/edit` and the rest of its pipeline. Local Whisper has no speaker separation and may drop some "uh/um", so say so when it matters.

## Use the result in a video
Reference the edited file from the storyboard as a `media` scene (`src`, `start`, `end`, `fit`, `audio`). Mix it with generated scenes (`story`, `title`, `photo`) for intro, cutaways and the call to action, then `videomaker build`.

Footage with a person on it stays on the user's machine; do not upload it anywhere without being asked.
