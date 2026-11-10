// Shared helpers. Scenes are pure functions of time: window.seek(t) draws frame t.
// No CSS transitions, no timers: that is what makes renders deterministic.
(() => {
  const root = document.documentElement.style;
  const S = window.STYLE;
  root.setProperty('--bg', S.background);
  root.setProperty('--bg2', S.background_to || S.background);
  root.setProperty('--fg', S.foreground);
  root.setProperty('--muted', S.muted);
  root.setProperty('--accent', S.accent);
  root.setProperty('--font', S.font);
  root.setProperty('--u', window.innerWidth / 100 + 'px');

  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  window.clamp = clamp;
  window.prog = (t, start, dur) => clamp((t - start) / dur);
  window.easeOut = (x) => 1 - Math.pow(1 - x, 3);
  window.easeOutBack = (x) => {
    const c1 = 1.4, c3 = c1 + 1;
    return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
  };
  // Fade the whole scene out on its last 0.3 s so cuts dip through the background.
  window.sceneAlpha = (t, fadeIn = 0.15) =>
    clamp(t / fadeIn) * clamp((window.DURATION - t) / 0.3);

  const stage = document.getElementById('stage');
  const glow = document.createElement('div');
  glow.id = 'glow';
  stage.appendChild(glow);
  const content = document.createElement('div');
  content.id = 'content';
  stage.appendChild(content);
  window.content = content;

  window.mk = (cls, text, parent = content) => {
    const e = document.createElement('div');
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    parent.appendChild(e);
    return e;
  };
  // Split text into word spans so they can be revealed one by one.
  window.words = (cls, text, parent = content) => {
    const box = window.mk(cls, null, parent);
    return text.split(/\s+/).filter(Boolean).map((w, i, a) => {
      const s = document.createElement('span');
      s.className = 'w';
      s.textContent = w + (i < a.length - 1 ? ' ' : '');
      box.appendChild(s);
      return s;
    });
  };
  window.reveal = (el, p) => {
    const e = window.easeOut(p);
    el.style.opacity = e;
    el.style.transform = `translateY(${(1 - e) * 0.5}em)`;
  };
  window.drawBackground = (t) => {
    const W = window.innerWidth, H = window.innerHeight;
    const a = t * 0.35;
    glow.style.left = W * (0.55 + 0.18 * Math.cos(a)) - glow.offsetWidth / 2 + 'px';
    glow.style.top = H * (0.35 + 0.12 * Math.sin(a * 1.3)) - glow.offsetHeight / 2 + 'px';
  };
})();
