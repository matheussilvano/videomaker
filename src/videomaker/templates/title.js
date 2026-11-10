(() => {
  const sc = window.SCENE;
  const bar = mk('bar');
  const ws = words('h1', sc.text);
  const sub = sc.subtitle ? mk('sub', sc.subtitle) : null;
  window.seek = (t) => {
    drawBackground(t);
    content.style.opacity = sceneAlpha(t);
    bar.style.width = prog(t, 0, 0.6) * 18 + 'vw';
    ws.forEach((w, i) => reveal(w, prog(t, 0.15 + i * 0.09, 0.45)));
    if (sub) reveal(sub, prog(t, 0.3 + ws.length * 0.09, 0.5));
  };
})();
