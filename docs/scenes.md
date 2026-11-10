# Custom scenes (`html`)

An `html` scene is a page you write. The renderer opens it in headless Chromium at the video size, then for each frame calls `window.seek(t)` and takes a screenshot.

```html
<!doctype html>
<meta charset="utf-8">
<body style="margin:0;background:#000">
<div id="x" style="color:#fff;font:120px sans-serif">hi</div>
<script>
  // Globals: SCENE (your JSON), STYLE, DURATION (s), FPS, HUD, CHARACTER
  window.seek = (t) => {
    document.getElementById('x').style.opacity = Math.min(1, t / 0.5);
  };
</script>
```
```json
{ "type": "html", "src": "scenes/hi.html", "duration": 3 }
```

Rules that keep renders reproducible: the whole frame is a function of `t`. No CSS transitions or animations, no `setTimeout`, no `Math.random()` (use a seeded generator), no network at render time (reference local files). Return after `seek` has applied the DOM changes; the renderer waits for fonts and for `window.imageReady` if you define it (a Promise).

For heavier motion design (3D, beat-synced music, springs) the optional `motion-design` skill covers a complete `seek(t)` engine; render its output to an mp4 and bring it in as a `media` scene.
