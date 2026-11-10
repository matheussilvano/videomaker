(() => {
  const sc = window.SCENE;
  const head = words('h1', sc.headline);
  const name = sc.name ? mk('h2', sc.name) : null;
  const pill = mk('pill', 'WhatsApp');
  const phone = mk('phone', sc.phone);
  const note = sc.note ? mk('note', sc.note) : null;
  window.seek = (t) => {
    drawBackground(t);
    content.style.opacity = sceneAlpha(t);
    head.forEach((w, i) => reveal(w, prog(t, 0.1 + i * 0.08, 0.45)));
    const n = 0.2 + head.length * 0.08;
    if (name) reveal(name, prog(t, n, 0.5));
    reveal(pill, prog(t, n + 0.3, 0.4));
    reveal(phone, prog(t, n + 0.5, 0.5));
    // gentle pulse on the number so the eye lands on it
    const pulse = 1 + 0.025 * Math.sin(Math.max(0, t - (n + 1)) * 5);
    phone.style.transform += ` scale(${pulse})`;
    phone.style.transformOrigin = 'left center';
    if (note) reveal(note, prog(t, n + 0.9, 0.5));
  };
})();
