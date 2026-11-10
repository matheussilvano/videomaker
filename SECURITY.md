# Security policy

Report vulnerabilities privately via GitHub Security Advisories on this repository (not public issues). Include a minimal reproduction with synthetic data.

## Model
- Videomaker runs locally. It makes network calls only when you ask: `videomaker setup` (model files from GitHub releases, verified by SHA-256 before use; upstream skills cloned at pinned commits) and any photo downloads you make yourself.
- Storyboards are data, not code, except `html` scenes: an `html` scene runs your page in a headless browser, so only render pages you trust.
- Scene text is placed into the page as text (not parsed as HTML) except where documented; paths in a storyboard are resolved relative to the storyboard file.
- Narration audio and footage never leave your machine. Transcription is local (faster-whisper).

## Known limits
`videomaker setup --skills` runs `uv sync` in the cloned video-use repository, which installs that project's dependencies. Review the pin before bumping it.
