(() => {
  const sc = window.SCENE;
  const head = sc.title ? words('h2', sc.title) : [];
  const rows = sc.items.map((text, i) => {
    const row = mk('item');
    const b = mk('badge', String(i + 1), row);
    const label = mk('', text, row);
    return { row, b, label };
  });
  // Spread the reveals across the scene so they follow the narration.
  const t0 = head.length ? 0.6 : 0.2;
  const gap = Math.min(0.9, Math.max(0.25, (window.DURATION - t0 - 1.0) / rows.length));
  window.seek = (t) => {
    drawBackground(t);
    content.style.opacity = sceneAlpha(t);
    head.forEach((w, i) => reveal(w, prog(t, 0.1 + i * 0.08, 0.4)));
    rows.forEach((r, i) => {
      const p = prog(t, t0 + i * gap, 0.45);
      reveal(r.row, p);
      r.b.style.transform = `scale(${0.6 + 0.4 * easeOutBack(p)})`;
    });
  };
})();
