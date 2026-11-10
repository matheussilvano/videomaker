// "story" scene: flat-illustration cartoon host + backdrop + photo card / info panel + top HUD.
// Pure function of time: window.seek(t). Mouth is driven by SCENE.env (narration loudness per frame).
(() => {
  const sc = window.SCENE;
  const HUD = window.HUD;
  const CH = window.CHARACTER;
  const W = window.innerWidth, H = window.innerHeight, u = W / 100;
  const FONT_H = "'Anton', 'Montserrat', sans-serif";
  const FONT_B = "'Montserrat', 'DejaVu Sans', sans-serif";

  const THEMES = {
    navy:     { wall: '#1f2b4d', wall2: '#2a3a66', floor: '#141b33', accent: '#f2b441', line: '#ffffff12' },
    germany:  { wall: '#262a33', wall2: '#363b49', floor: '#16181e', accent: '#f2c230', line: '#ffffff10' },
    belgium:  { wall: '#2b2b35', wall2: '#3c3a30', floor: '#17171d', accent: '#f6d04d', line: '#ffffff10' },
    portugal: { wall: '#1d3b36', wall2: '#2a5046', floor: '#102421', accent: '#ef5b4a', line: '#ffffff10' },
    gold:     { wall: '#3a2f1c', wall2: '#5a4624', floor: '#201a0e', accent: '#ffd36b', line: '#ffffff10' },
  };
  const T = THEMES[sc.backdrop] || THEMES.navy;

  const stage = document.getElementById('stage');
  stage.style.cssText = `position:absolute;inset:0;overflow:hidden;padding:0;gap:0;display:block;background:${T.wall}`;
  document.getElementById('glow').remove();
  window.content.remove();

  const el = (tag, css, parent = stage, html) => {
    const e = document.createElement(tag);
    e.style.cssText = css;
    if (html != null) e.innerHTML = html;
    parent.appendChild(e);
    return e;
  };
  const FLOOR = H * 0.79;

  // ---- backdrop: flat wall, tile lines, soft skyline, floor
  el('div', `position:absolute;inset:0 0 ${H - FLOOR}px 0;background:linear-gradient(180deg,${T.wall2},${T.wall});`);
  el('div', `position:absolute;inset:0 0 ${H - FLOOR}px 0;background-image:linear-gradient(${T.line} 2px,transparent 2px),linear-gradient(90deg,${T.line} 2px,transparent 2px);background-size:${u * 9}px ${u * 9}px;`);
  const sky = el('svg', `position:absolute;left:0;top:${FLOOR - u * 30}px;width:${W}px;height:${u * 30}px;opacity:.5`);
  sky.setAttribute('viewBox', '0 0 100 30');
  sky.setAttribute('preserveAspectRatio', 'none');
  let skyline = '';
  for (let i = 0, x = -2; x < 104; i++) {
    const w = 7 + ((i * 5) % 7), h = 10 + ((i * 11) % 15);
    skyline += `<rect x="${x}" y="${30 - h}" width="${w}" height="${h}" fill="${T.wall}"/>`;
    if (i % 2 === 0) skyline += `<polygon points="${x},${30 - h} ${x + w / 2},${30 - h - 5} ${x + w},${30 - h}" fill="${T.wall}"/>`;
    x += w + 0.6;
  }
  sky.innerHTML = skyline;
  el('div', `position:absolute;left:0;right:0;top:${FLOOR}px;bottom:0;background:${T.floor};`);
  el('div', `position:absolute;left:0;right:0;top:${FLOOR}px;height:${u * 0.7}px;background:${T.accent};opacity:.55`);

  // ---- HUD (top info bar)
  let hud = null;
  if (HUD) {
    hud = el('div', `position:absolute;left:${u * 4}px;right:${u * 4}px;top:${H * 0.045}px;height:${u * 12.5}px;border-radius:${u * 4.2}px;background:rgba(14,18,32,.94);display:flex;align-items:center;padding:0 ${u * 3.2}px;gap:${u * 2.6}px;box-shadow:0 ${u}px ${u * 3}px rgba(0,0,0,.35);font-family:${FONT_B};color:#fff`);
    el('div', `flex:none;width:${u * 8}px;height:${u * 9.6}px;background:${T.accent};clip-path:polygon(0 0,100% 0,100% 68%,50% 100%,0 68%);display:grid;place-items:center;color:#1a1a22;font:${u * 3.6}px/1 ${FONT_H}`, hud, HUD.badge);
    el('div', 'display:flex;flex-direction:column;gap:' + u * 0.6 + 'px;flex:1;min-width:0', hud,
      `<div style="font:${u * 4.2}px/1 ${FONT_H};letter-spacing:.02em">${HUD.title}</div>` +
      (HUD.subtitle ? `<div style="font:700 ${u * 1.9}px/1.1 ${FONT_B};color:#9aa3bd;letter-spacing:.06em">${HUD.subtitle}</div>` : ''));
    if (HUD.right_top || HUD.right_bottom) {
      el('div', `flex:none;width:2px;height:${u * 8}px;background:#ffffff22`, hud);
      el('div', `flex:none;display:flex;flex-direction:column;align-items:flex-end;gap:${u * 0.8}px`, hud,
        (HUD.right_top ? `<div style="font:${u * 3.8}px/1 ${FONT_H}">${HUD.right_top}</div>` : '') +
        (HUD.right_bottom ? `<div class="pulse" style="font:800 ${u * 1.9}px/1 ${FONT_B};background:#ef4444;border-radius:99px;padding:${u * 0.7}px ${u * 1.6}px;letter-spacing:.05em">${HUD.right_bottom}</div>` : ''));
    }
  }
  const pulseEl = hud && hud.querySelector('.pulse');

  // ---- chip (tilted tag) + place pill
  const chip = sc.chip ? el('div', `position:absolute;left:${u * 7}px;top:${H * 0.165}px;transform:rotate(-6deg);background:${T.accent};color:#1a1a22;border-radius:${u * 1.2}px;padding:${u * 1.2}px ${u * 2.4}px;font:${u * 3.8}px/1 ${FONT_H};letter-spacing:.03em`, stage, sc.chip) : null;
  const place = sc.place ? el('div', `position:absolute;left:50%;top:${H * 0.165}px;transform:translateX(-50%);background:rgba(14,18,32,.92);color:#fff;border-radius:${u * 1.8}px;padding:${u * 1.5}px ${u * 3}px;font:${u * 4.2}px/1 ${FONT_H};letter-spacing:.03em;white-space:nowrap`, stage, sc.place) : null;

  // ---- headline (big text on empty backdrops): title and subtitle share one column
  const hl = (sc.headline || sc.headline_sub)
    ? el('div', `position:absolute;left:${u * 6}px;right:${u * 6}px;top:${H * 0.2}px;display:flex;flex-direction:column;align-items:center;gap:${u * 2.4}px;text-align:center`)
    : null;
  const head = sc.headline ? el('div', `color:#fff;font:${u * 15}px/1.02 ${FONT_H};text-transform:uppercase;text-shadow:0 ${u * .6}px 0 rgba(0,0,0,.35)`, hl, sc.headline) : null;
  const headSub = sc.headline_sub ? el('div', `color:${T.accent};font:700 ${u * 4.6}px/1.2 ${FONT_B};letter-spacing:.08em;text-transform:uppercase`, hl, sc.headline_sub) : null;

  // ---- photo card
  let card = null, cardImg = null, credit = null;
  const cardTop = H * 0.225, cardH = H * 0.325;
  if (sc.card) {
    card = el('div', `position:absolute;left:${u * 8}px;right:${u * 8}px;top:${cardTop}px;height:${cardH}px;border:${u * 0.9}px solid ${T.accent};border-radius:${u * 3}px;overflow:hidden;background:#000;box-shadow:0 ${u * 2}px ${u * 5}px rgba(0,0,0,.5)`);
    cardImg = el('img', `position:absolute;inset:-4%;width:108%;height:108%;object-fit:cover;object-position:${sc.card.focus}`, card);
    cardImg.src = sc.card.src_url;
    if (sc.card.credit) credit = el('div', `position:absolute;right:${u * 9}px;top:${cardTop + cardH + u * 1}px;font:${u * 1.7}px/1 ${FONT_B};color:#ffffff99`, stage, sc.card.credit);
  }

  // ---- info panel ("group table" look)
  let panel = null, rowEls = [];
  if (sc.panel) {
    const P = sc.panel;
    const FLAGS = {
      de: 'linear-gradient(180deg,#111 0 33.3%,#d62d20 33.3% 66.6%,#ffcd00 66.6%)',
      be: 'linear-gradient(90deg,#111 0 33.3%,#ffd90c 33.3% 66.6%,#ef3340 66.6%)',
      pt: 'linear-gradient(90deg,#046a38 0 40%,#da291c 40%)',
    };
    panel = el('div', `position:absolute;left:${u * 8}px;right:${u * 8}px;top:${H * 0.2}px;border:${u * 0.8}px solid #6fa8ff;border-radius:${u * 3}px;background:#141a30f2;padding:${u * 3.4}px ${u * 3}px;display:flex;flex-direction:column;gap:${u * 1.6}px;box-shadow:0 ${u * 2}px ${u * 5}px rgba(0,0,0,.45)`);
    el('div', `text-align:center;color:${T.accent};font:${u * 7.2}px/1 ${FONT_H};letter-spacing:.02em;text-transform:uppercase`, panel, P.title);
    if (P.subtitle) el('div', `text-align:center;color:#c9d0e6;font:800 ${u * 2.3}px/1 ${FONT_B};letter-spacing:.12em;text-transform:uppercase`, panel, P.subtitle);
    P.rows.forEach((r) => {
      const row = el('div', `display:flex;align-items:center;gap:${u * 2.4}px;background:#25304f;border-radius:${u * 1.4}px;padding:${u * 1.8}px ${u * 2.4}px;font-family:${FONT_B}`, panel);
      if (r.flag) el('div', `flex:none;width:${u * 7}px;height:${u * 4.6}px;border-radius:${u * .5}px;background:${FLAGS[r.flag]};box-shadow:0 0 0 2px #ffffff22`, row);
      el('div', `flex:1;color:#fff;font:${u * 4}px/1.05 ${FONT_H};text-transform:uppercase;letter-spacing:.02em`, row, r.text);
      if (r.value) el('div', `flex:none;color:#b7bfd8;font:800 ${u * 2.4}px/1.15 ${FONT_B};text-align:right;max-width:${u * 34}px`, row, r.value);
      rowEls.push(row);
    });
    if (P.big) el('div', `text-align:center;color:#fff;font:${u * 10.5}px/1 ${FONT_H};letter-spacing:.01em;margin-top:${u * 1}px;background:#25d366;color:#05301a;border-radius:${u * 2}px;padding:${u * 2.2}px 0`, panel, P.big);
  }

  // ---- the cartoon host (inline SVG, local coords: body centre x=100, feet y=410)
  const skin = CH.skin, hair = CH.hair, robe = CH.robe, trim = CH.trim;
  const shade = 'rgba(60,40,10,.10)';
  const svgW = u * 52, svgH = svgW * (500 / 360);
  const bob = el('div', `position:absolute;width:${svgW}px;height:${svgH}px;will-change:transform`);
  bob.innerHTML = `
  <svg viewBox="-80 -70 360 500" width="${svgW}" height="${svgH}" style="overflow:visible">
    <ellipse cx="100" cy="408" rx="78" ry="11" fill="rgba(0,0,0,.35)"/>
    <ellipse cx="72" cy="402" rx="22" ry="9" fill="#1b1b22"/><ellipse cx="128" cy="402" rx="22" ry="9" fill="#1b1b22"/>
    <rect x="88" y="130" width="24" height="26" rx="8" fill="${skin}"/>
    <path d="M50 158 Q100 128 150 158 L170 398 Q100 412 30 398 Z" fill="${robe}"/>
    <path d="M100 150 L170 398 Q100 412 100 405 Z" fill="${shade}"/>
    <rect x="92" y="150" width="16" height="250" fill="${trim}"/>
    <rect x="96" y="150" width="3" height="250" fill="rgba(255,255,255,.35)"/>
    <path d="M68 152 L100 214 L132 152" fill="none" stroke="${trim}" stroke-width="10" stroke-linejoin="round"/>
    <rect x="31" y="382" width="138" height="12" rx="4" fill="${trim}"/>
    <rect x="94" y="232" width="12" height="46" rx="2" fill="#fff6d6"/><rect x="82" y="244" width="36" height="12" rx="2" fill="#fff6d6"/>
    ${CH.collar ? '<rect x="82" y="144" width="36" height="11" rx="4" fill="#17171f"/><rect x="95" y="145" width="10" height="7" rx="1.5" fill="#fff"/>' : ''}
    <g id="armR"><rect x="128" y="152" width="26" height="112" rx="13" fill="${robe}" stroke="#d9d0bb" stroke-width="2"/><rect x="128" y="236" width="26" height="8" fill="${trim}"/><circle cx="141" cy="272" r="14.5" fill="${skin}"/></g>
    <g id="armL"><rect x="46" y="152" width="26" height="112" rx="13" fill="${robe}" stroke="#d9d0bb" stroke-width="2"/><rect x="46" y="236" width="26" height="8" fill="${trim}"/><circle cx="59" cy="272" r="14.5" fill="${skin}"/></g>
    <circle cx="50" cy="92" r="9" fill="${skin}"/><circle cx="150" cy="92" r="9" fill="${skin}"/>
    <circle cx="100" cy="88" r="51" fill="${skin}"/>
    <path d="M49 86 C45 36 92 24 116 30 C146 34 156 60 151 86 C144 64 128 54 106 56 C84 56 62 62 49 86 Z" fill="${hair}"/>
    <g id="brows" fill="none" stroke="${hair}" stroke-width="4.5" stroke-linecap="round"><path d="M67 80 Q80 72 93 79"/><path d="M107 79 Q120 72 133 80"/></g>
    <ellipse id="eyeL" cx="80" cy="94" rx="5.8" ry="6.8" fill="#1b1b1b"/><ellipse id="eyeR" cx="120" cy="94" rx="5.8" ry="6.8" fill="#1b1b1b"/>
    <path d="M99 101 Q104 113 109 105" fill="none" stroke="rgba(120,70,40,.55)" stroke-width="3" stroke-linecap="round"/>
    <circle cx="66" cy="110" r="9" fill="#ee8f7a" opacity=".32"/><circle cx="134" cy="110" r="9" fill="#ee8f7a" opacity=".32"/>
    <path d="M78 113 Q100 134 122 113" fill="none" stroke="#6b2c20" stroke-width="4.5" stroke-linecap="round"/>
    <ellipse id="mouth" cx="100" cy="120" rx="15" ry="0.1" fill="#4a1914"/>
  </svg>`;
  const $ = (id) => bob.querySelector('#' + id);
  const armR = $('armR'), armL = $('armL'), eyeL = $('eyeL'), eyeR = $('eyeR'), mouth = $('mouth'), brows = $('brows');
  const cx = sc.side === 'left' ? W * 0.28 : sc.side === 'right' ? W * 0.72 : W * 0.5;
  const baseLeft = cx - svgW * (180 / 360);   // body centre x=100 -> 180/360 of the viewBox
  const baseTop = FLOOR + u * 1.2 - svgH * ((410 + 70) / 500);
  bob.style.left = baseLeft + 'px';
  bob.style.top = baseTop + 'px';

  const D = window.DURATION, FPS = window.FPS || 30;
  const env = sc.env || [];
  const rot = (g, a, x, y) => g.setAttribute('transform', `rotate(${a} ${x} ${y})`);
  const lerp = (a, b, k) => a + (b - a) * k;

  window.seek = (t) => {
    const a = sceneAlpha(t, 0.12);
    stage.style.opacity = a;

    // entrance: host slides in with a little overshoot, then bobs
    const k = prog(t, 0.05, 0.55);
    const slide = (1 - easeOutBack(k)) * (sc.side === 'left' ? -1 : 1) * u * 40;
    const hop = Math.abs(Math.sin(t * 3.1)) * u * 0.55;
    bob.style.transform = `translate(${sc.side === 'center' ? 0 : slide}px, ${(sc.side === 'center' ? (1 - easeOutBack(k)) * u * 30 : 0) - hop}px)`;

    // arms by pose; angle>0 swings the arm to the viewer's left, <0 to the right
    const sway = Math.sin(t * 2.4) * 3;
    let aL = 7 + sway, aR = -7 - sway;
    const toward = sc.side === 'left' ? 'R' : 'L';   // arm on the side facing the card/centre
    const raise = easeOutBack(prog(t, 0.35, 0.45));
    if (sc.pose === 'point') {
      const ang = lerp(7, 148 + Math.sin(t * 6) * 4, raise);
      if (toward === 'R') aR = -ang; else aL = ang;
    } else if (sc.pose === 'wave') {
      aR = -lerp(7, 140 + Math.sin(t * 9) * 16, raise);
    } else if (sc.pose === 'cheer') {
      const up = 150 + Math.sin(t * 7) * 8;
      aL = lerp(7, up, raise); aR = -lerp(7, up, raise);
    }
    rot(armL, aL, 59, 160); rot(armR, aR, 141, 160);

    // blink every ~3 s
    const bl = (t % 3.1);
    const closed = bl > 2.95 && bl < 3.05 ? 0.08 : 1;
    eyeL.setAttribute('ry', 6.8 * closed); eyeR.setAttribute('ry', 6.8 * closed);
    brows.setAttribute('transform', `translate(0 ${Math.sin(t * 2) * 0.8})`);

    // mouth from narration loudness (0..1 per frame, lightly smoothed)
    const i = Math.min(env.length - 1, Math.floor(t * FPS));
    const v = env.length ? (env[Math.max(0, i)] * 0.6 + env[Math.max(0, i - 1)] * 0.4) : 0;
    mouth.setAttribute('ry', Math.max(0.1, v * 15));

    // pieces
    if (hud) { const p = prog(t, 0, 0.4); hud.style.opacity = easeOut(p); hud.style.transform = `translateY(${(1 - easeOut(p)) * -u * 6}px)`; }
    if (pulseEl) pulseEl.style.transform = `scale(${1 + 0.07 * Math.sin(t * 6)})`;
    if (chip) { const p = easeOutBack(prog(t, 0.15, 0.4)); chip.style.transform = `rotate(-6deg) scale(${p})`; }
    if (place) { const p = easeOutBack(prog(t, 0.25, 0.4)); place.style.transform = `translateX(-50%) scale(${p})`; }
    if (head) { reveal(head, prog(t, 0.1, 0.5)); head.style.transform = `translateY(${(1 - easeOut(prog(t, 0.1, 0.5))) * 3 * u}px) scale(${1 + 0.02 * Math.sin(t * 2)})`; }
    if (headSub) reveal(headSub, prog(t, 0.45, 0.5));
    if (card) {
      const p = easeOutBack(prog(t, 0.1, 0.55));
      card.style.transform = `scale(${0.85 + 0.15 * p}) rotate(${(1 - p) * -3}deg)`;
      card.style.opacity = clamp(prog(t, 0.1, 0.3));
      const zoom = 1 + 0.07 * clamp(t / D);
      cardImg.style.transform = `scale(${zoom})`;
      if (credit) credit.style.opacity = clamp(prog(t, 0.5, 0.4));
    }
    if (panel) {
      const p = easeOutBack(prog(t, 0.1, 0.5));
      panel.style.transform = `scale(${0.88 + 0.12 * p})`;
      panel.style.opacity = clamp(prog(t, 0.1, 0.3));
      rowEls.forEach((r, n) => reveal(r, prog(t, 0.35 + n * 0.12, 0.35)));
    }
  };
})();
