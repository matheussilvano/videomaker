(() => {
  const sc = window.SCENE;
  const stage = document.getElementById('stage');
  stage.style.background = '#000';
  document.getElementById('glow').remove();
  window.content.remove();
  const img = document.createElement('img');
  img.className = 'photo';
  img.src = sc.src_url;
  img.style.objectPosition = sc.focus;
  let card = null;
  if (sc.fit === 'card') {
    // Small or low-resolution photo: blurred copy fills the frame, sharp copy sits in a card.
    img.style.filter = 'blur(' + window.innerWidth * 0.035 + 'px) brightness(.55)';
    card = document.createElement('img');
    card.src = sc.src_url;
    card.style.cssText = 'position:absolute;left:12%;width:76%;top:9%;aspect-ratio:1/1;object-fit:cover;' +
      'border-radius:6vw;box-shadow:0 3vw 8vw rgba(0,0,0,.55);object-position:' + sc.focus;
    stage.appendChild(img);
    stage.appendChild(card);
  } else {
    stage.appendChild(img);
  }
  const shade = document.createElement('div');
  shade.className = 'shade';
  stage.appendChild(shade);
  const lower = document.createElement('div');
  lower.className = 'lower';
  stage.appendChild(lower);
  const bar = mk('bar', null, lower);
  const title = sc.title ? words('h1', sc.title, lower) : [];
  const sub = sc.subtitle ? mk('sub', sc.subtitle, lower) : null;
  if (sc.credit) { const c = document.createElement('div'); c.className = 'credit'; c.textContent = sc.credit; stage.appendChild(c); }
  window.imageReady = Promise.all([img.decode(), card ? card.decode() : 0]).catch(() => {});
  const D = window.DURATION;
  window.seek = (t) => {
    const k = clamp(t / D);
    const e = k * k * (3 - 2 * k);
    let s = 1, x = 0;
    if (sc.motion === 'zoom-in') s = 1 + 0.12 * e;
    else if (sc.motion === 'zoom-out') s = 1.12 - 0.12 * e;
    else { s = 1.08; x = (sc.motion === 'pan-left' ? -1 : 1) * (2.5 - 5 * e); }
    img.style.transform = `translateX(${x}%) scale(${s})`;
    if (card) card.style.transform = `scale(${1 + 0.04 * e})`;
    stage.style.opacity = sceneAlpha(t, 0.2);
    bar.style.width = prog(t, 0.2, 0.6) * 14 + 'vw';
    title.forEach((w, i) => reveal(w, prog(t, 0.3 + i * 0.08, 0.45)));
    if (sub) reveal(sub, prog(t, 0.5 + title.length * 0.08, 0.5));
  };
})();
