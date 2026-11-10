(() => {
  const sc = window.SCENE;
  const mark = mk('quote-mark', '“');
  const ws = words('quote', sc.text);
  const who = sc.author ? mk('author', '— ' + sc.author) : null;
  window.seek = (t) => {
    drawBackground(t);
    content.style.opacity = sceneAlpha(t);
    reveal(mark, prog(t, 0, 0.5));
    ws.forEach((w, i) => reveal(w, prog(t, 0.2 + i * 0.07, 0.4)));
    if (who) reveal(who, prog(t, 0.4 + ws.length * 0.07, 0.5));
  };
})();
