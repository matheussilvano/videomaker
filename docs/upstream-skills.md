# Upstream skills

`videomaker setup --skills` links two MIT-licensed community skills next to this one. Both are pinned to a full commit in `src/videomaker/install.py`; setup never follows a moving branch and never overwrites a skill you already have.

| Skill | Used for | Pin |
| --- | --- | --- |
| [video-use](https://github.com/browser-use/video-use) | cutting raw footage by transcript, grading, subtitles | see `install.py` |
| [claude-motion-design](https://github.com/howseen-ai/claude-motion-design) | bespoke code-only motion (3D, beat sync) | see `install.py` |

video-use transcribes with ElevenLabs Scribe by default. `videomaker transcribe` writes the same JSON with local Whisper, so it works without a key.

Bumping a pin: read the upstream diff, run `make check`, and list what you read in the PR.
