(() => {
  const sc = window.SCENE;
  // Count up when the value looks like "<prefix><number><suffix>", e.g. "$1.2M" or "90%".
  const m = /^([^0-9-]*)(-?[0-9][0-9.,]*)(.*)$/.exec(sc.value);
  const num = m ? parseFloat(m[2].replace(/,/g, '')) : NaN;
  const decimals = m && m[2].includes('.') ? m[2].split('.')[1].length : 0;
  const big = mk('stat', sc.value);
  const label = mk('h2', sc.label);
  window.seek = (t) => {
    drawBackground(t);
    content.style.opacity = sceneAlpha(t);
    const p = prog(t, 0.1, 1.2);
    if (m && Number.isFinite(num)) {
      big.textContent = m[1] + (num * easeOut(p)).toFixed(decimals) + m[3];
    }
    big.style.transform = `scale(${0.85 + 0.15 * easeOutBack(prog(t, 0, 0.6))})`;
    big.style.transformOrigin = 'left center';
    reveal(label, prog(t, 0.5, 0.5));
  };
})();
