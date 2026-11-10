# Narration

Voices come from [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) (82M parameters, ONNX, CPU). `videomaker setup --models` downloads about 120 MB once to `~/.cache/videomaker/models` (override with `VIDEOMAKER_HOME`); each file is SHA-256 verified.

| language | default voice | others |
| --- | --- | --- |
| `en` | `af_heart` | `am_michael`, `bf_emma`, ... |
| `pt` / `pt-br` | `pf_dora` | `pm_alex`, `pm_santa` |
| `es` `fr` `it` `hi` `ja` `zh` | one default each | `videomaker voices` |

A narration of 3 s takes about 1 s to synthesize on a laptop CPU. Numbers and phone digits: write them as words in `narration` (the model reads digits unreliably) and keep digits in `caption_text`.

Quality is good for ads and explainers, not studio. To use your own voice, record it and put the file through the `footage` skill, or set `voice.engine` to `none` and give each scene a `duration`.
