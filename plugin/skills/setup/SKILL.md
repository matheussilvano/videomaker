---
name: setup
description: Install or diagnose videomaker (ffmpeg, browser, free narration voices, video-use and motion-design skills). Use when `videomaker` is missing, `doctor` reports a failure, or the user asks to set it up.
---

# Set up videomaker

1. `videomaker --version`. If the command is missing: `uv tool install git+https://github.com/matheussilvano/videomaker` (needs [uv](https://docs.astral.sh/uv/)).
2. `videomaker doctor`. Required: ffmpeg + ffprobe (with libx264, libass `ass`, `loudnorm`) and a browser. Install ffmpeg with the system package manager (ask before using sudo).
3. Fix what is missing:
   - `videomaker setup --browser` (Playwright Chromium; an installed Google Chrome also works).
   - `videomaker setup --models` (about 120 MB of Kokoro narration voices, SHA-256 verified).
   - `videomaker setup --skills` (video-use for footage, motion-design for bespoke motion; pinned commits, existing skills are never overwritten).
   - Local transcription for the `footage` skill: `uv tool install --force 'videomaker[asr] @ git+https://github.com/matheussilvano/videomaker'`.
4. Re-run `videomaker doctor` and report exactly what is ready. Restart Claude Code after new skills are linked.

Everything runs locally; no account or API key is needed.
