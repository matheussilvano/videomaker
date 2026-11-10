# Architecture

```mermaid
flowchart LR
  SB[storyboard.json] --> V[validate: pydantic]
  V --> N[narration: Kokoro -> WAV per scene]
  N --> D[durations: speech + hold]
  D --> R{scene type}
  R -->|story/title/photo/...| H[HTML + seek t -> Playwright PNGs -> ffmpeg]
  R -->|media| F[ffmpeg trim/scale/pad]
  H --> S[segment mp4 with audio, cached]
  F --> S
  S --> J[lossless concat -c copy]
  J --> M[music duck + loudnorm]
  M --> C[captions burned last]
  C --> OUT[final.mp4 + captions.srt]
```

- **One recipe per segment.** Every segment is H.264/AAC with identical parameters, so joining is `-c copy` and nothing is encoded twice.
- **Cache key** = scene JSON, format, style, HUD, character, measured audio length, source file size/mtime, template hash and tool version. Edit one scene and only that scene re-renders.
- **Narration drives time.** Speech length decides the scene length; the host's mouth uses the narration loudness per frame (`assemble.mouth_envelope`).
- **Captions** are timed proportionally to word length inside each narration. That is accurate to a fraction of a second per cue, not word-aligned (see roadmap).
- **Skills** (`plugin/skills`) are the agent's playbook; the Python package is the engine. The agent never needs to write ffmpeg commands.
