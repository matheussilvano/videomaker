# Contributing

Thanks for helping! You do not need any account or API key: everything runs locally.

## 5-minute start
```bash
git clone https://github.com/matheussilvano/videomaker && cd videomaker
make setup      # uv sync + browser + narration models
make check      # ruff + mypy + pytest (what CI runs)
make demo       # builds examples/demo-en into out/demo/final.mp4
```
Pick an issue labelled [`good first issue`](https://github.com/matheussilvano/videomaker/labels/good%20first%20issue), comment that you are taking it, open a draft PR early.

## Where things live
| I want to... | Touch |
| --- | --- |
| add a scene type | `storyboard.py` (model) + `templates/<type>.js` + `assemble.py` (asset paths) + `docs/storyboard.md` + a test |
| change how the host looks or moves | `templates/story.js` (SVG + `seek(t)`) |
| add a narration language or voice | `tts.py` (`LANGUAGES`) |
| change captions | `captions.py` |
| change how a video is joined or mixed | `assemble.py` (`_finish`) |
| improve the Claude skills | `plugin/skills/*/SKILL.md` |

## Rules
1. Scenes are pure functions of time (`window.seek(t)`): no CSS transitions, no timers, no `Math.random()` without a seed. That is what keeps renders reproducible.
2. Every scene segment is encoded with the same recipe (`media.VIDEO_ARGS` / `AUDIO_ARGS`) so the final join stays a lossless `-c copy`. Captions are burned last.
3. Tests: `uv run pytest`. Browser tests are skipped when no Chromium/Chrome exists. Add a test that fails without your change.
4. `uv run ruff format src tests` and `uv run ruff check src tests` and `uv run mypy src` must pass.
5. **No real people or private data in the repo**: no personal photos, phone numbers or screenshots; examples use synthetic or generic content. Photos need a free license and a credit.
6. Upstream skills are pinned by full commit in `install.py`. Bump a pin only after reading the diff, and say what you read in the PR.
7. Small PRs, short imperative commit messages.
