// Clause Board kit: flat index cards on a dark navy study board, teal article tabs, amber marker swipes,
// coral stamps, dashed connectors, exam-ticket chips and the PYQ question card.
// All pure functions of their arguments (no state between frames). Fonts: 'Inter' 900 (display), 'Mono' 700 (labels).
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rnd, rr, circle, line, TAU } from './lib.js';

// ---------- background ----------
/** the board: deep navy, a faint dot grid that drifts slowly, a darker margin band at the top */
export function board(t = 0) {
  ctx.fillStyle = C.board; ctx.fillRect(-300, -300, W + 600, H + 600);
  const off = (t * 6) % 60;
  ctx.fillStyle = C.boardDot;
  for (let y = -300 + off; y < H + 300; y += 60) for (let x = -300; x < W + 300; x += 60) { ctx.beginPath(); ctx.arc(x, y, 3, 0, TAU); ctx.fill(); }
  ctx.fillStyle = C.boardDeep; ctx.fillRect(-300, -300, W + 600, 480);
}

// ---------- text helpers ----------
export function mono(text, x, y, size, fill = C.ink, align = 'left', spacing = 2) {
  ctx.font = `700 ${size}px Mono`; ctx.letterSpacing = `${spacing}px`; ctx.textAlign = align; ctx.textBaseline = 'middle';
  ctx.fillStyle = fill; ctx.fillText(text, x, y); ctx.letterSpacing = '0px';
}
export function disp(text, x, y, size, fill = C.ink, align = 'center', spacing = -2) {
  ctx.font = `900 ${size}px Inter`; ctx.letterSpacing = `${spacing}px`; ctx.textAlign = align; ctx.textBaseline = 'middle';
  ctx.fillStyle = fill; ctx.fillText(text, x, y); ctx.letterSpacing = '0px';
}
export function measure(text, size, font = 'Inter', weight = 900, spacing = -2) {
  ctx.font = `${weight} ${size}px ${font}`; ctx.letterSpacing = `${spacing}px`; const w = ctx.measureText(text).width; ctx.letterSpacing = '0px'; return w;
}

// ---------- signature motion: the "deal" ----------
/** card dealt in from the right edge (never crosses the caption zone): returns {x, y, rot, a} for progress p (0..1) toward (x, y). k = index for varied tilt */
export function deal(p, x, y, k = 0) {
  const e = eob(clamp(p));
  return { x: lerp(x + 1150, x, e), y: y + (1 - e) * (rnd(k) - 0.5) * 260, rot: (1 - e) * (rnd(k + 9) - 0.5) * 0.5 + (rnd(k + 3) - 0.5) * 0.04, a: clamp(p * 4) };
}

// ---------- components ----------
/** index card: ivory, flat bottom shade, faint ruled lines, red-free; centre x, y */
export function card(x, y, w, h, rot = 0, { ruled = true, tab = null } = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = C.boardDeep; rr(-w / 2 + 10, -h / 2 + 16, w, h, 18); ctx.fill();          // flat drop (one darker tone)
  ctx.fillStyle = C.cardShade; rr(-w / 2, -h / 2 + 8, w, h, 18); ctx.fill();
  ctx.fillStyle = C.card; rr(-w / 2, -h / 2, w, h, 18); ctx.fill();
  if (ruled) { ctx.fillStyle = C.cardLine; for (let yy = -h / 2 + 110; yy < h / 2 - 30; yy += 64) ctx.fillRect(-w / 2 + 36, yy, w - 72, 3); }
  if (tab) { ctx.fillStyle = C.teal; rr(-w / 2 + 36, -h / 2 - 34, measure(tab, 34, 'Mono', 700, 3) + 44, 56, 12); ctx.fill(); mono(tab, -w / 2 + 58, -h / 2 - 6, 34, C.white, 'left', 3); }
  ctx.restore();
}
/** the big teal article tab: small "ARTICLE" over a huge number; stamp-slams in with scale s */
export function articleTab(num, x, y, s = 1, label = 'ARTICLE') {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const w = Math.max(420, measure(num, 260) + 120), h = 380;
  ctx.fillStyle = C.tealDark; rr(-w / 2, -h / 2 + 14, w, h, 34); ctx.fill();
  ctx.fillStyle = C.teal; rr(-w / 2, -h / 2, w, h, 34); ctx.fill();
  mono(label, 0, -h / 2 + 62, 44, C.board, 'center', 10);
  disp(num, 0, 40, 260, C.white);
  ctx.restore();
}
/** amber marker swipe behind text: p 0..1 draws left to right. Slightly ragged ends (flat). */
export function marker(x, y, w, h, p, color = C.amber) {
  if (p <= 0) return;
  const ww = w * eo(clamp(p));
  ctx.fillStyle = color; ctx.beginPath();
  ctx.moveTo(x, y + 6); ctx.lineTo(x + ww, y); ctx.lineTo(x + ww - 6, y + h); ctx.lineTo(x + 4, y + h - 4); ctx.closePath(); ctx.fill();
}
/** coral rubber stamp (rotated outline box + text), slams with scale */
export function stamp(text, x, y, size, rot = -0.14, sc = 1, color = C.coral) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sc, sc);
  const w = measure(text, size, 'Inter', 900, 4) + size * 0.9, h = size * 1.55;
  ctx.strokeStyle = color; ctx.lineWidth = size * 0.12; rr(-w / 2, -h / 2, w, h, size * 0.2); ctx.stroke();
  ctx.lineWidth = size * 0.05; rr(-w / 2 + size * 0.18, -h / 2 + size * 0.18, w - size * 0.36, h - size * 0.36, size * 0.12); ctx.stroke();
  disp(text, 0, size * 0.04, size, color, 'center', 4);
  ctx.restore();
}
/** dashed connector drawn from a to b (with a round node at each end), p 0..1 */
export function connector(ax, ay, bx, by, p, color = C.slate) {
  if (p <= 0) return;
  const e = eio(clamp(p)), ex = lerp(ax, bx, e), ey = lerp(ay, by, e);
  ctx.setLineDash([22, 16]); line([[ax, ay], [ex, ey]], color, 8); ctx.setLineDash([]);
  circle(ax, ay, 14, color); if (p >= 1) circle(bx, by, 14, color);
}
/** exam ticket chip: ink body, notches cut on both sides, exam in mono, year in amber. centre x, y */
export function chip(exam, year, x, y, s = 1, a = 1) {
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s);
  const ew = measure(exam, 40, 'Mono', 700, 2), yw = measure(year, 52, 'Inter', 900, -1), w = ew + yw + 120, h = 104;
  ctx.fillStyle = C.boardDeep; rr(-w / 2 + 6, -h / 2 + 10, w, h, 16); ctx.fill();
  ctx.fillStyle = C.card; rr(-w / 2, -h / 2, w, h, 16); ctx.fill();
  ctx.fillStyle = C.ink; rr(-w / 2 + ew + 56, -h / 2, w - ew - 56, h, [0, 16, 16, 0]); ctx.fill();
  ctx.fillStyle = C.board; circle(-w / 2, 0, 16, C.board); circle(w / 2, 0, 16, C.board);   // ticket notches
  ctx.setLineDash([6, 8]); line([[-w / 2 + ew + 56, -h / 2 + 12], [-w / 2 + ew + 56, h / 2 - 12]], C.slate, 3); ctx.setLineDash([]);
  mono(exam, -w / 2 + 28, 2, 40, C.ink, 'left', 2);
  disp(year, -w / 2 + ew + 56 + (w - ew - 56) / 2, 3, 52, C.amber, 'center', -1);
  ctx.restore();
}
/** the PYQ question card: exam label tab, question lines, four option rows (a)-(d); rows deal in with p (0..1 each row) */
export function pyqCard(x, y, { exam, lines, opts }, p = 1, rowP = [1, 1, 1, 1], rot = 0) {
  const w = 960, h = 1000;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  card(0, 0, w, h, 0, { ruled: false, tab: exam });
  ctx.save(); ctx.translate(-w / 2 + 50, -h / 2 + 90);
  lines.forEach((ln, i) => {
    const hl = ln.startsWith('*'); const tx = hl ? ln.slice(1) : ln;
    if (hl) marker(-8, i * 64 - 26, measure(tx, 44, 'Inter', 900, -1) + 16, 56, 1, C.amberSoft);
    disp(tx, 0, i * 64, 44, C.ink, 'left', -1);
  });
  ctx.restore();
  const oy = -h / 2 + 140 + lines.length * 64;
  opts.forEach((o, i) => {
    const q = clamp(rowP[i] ?? 1); if (q <= 0) return;
    const yy = oy + i * 112, xo = (1 - eo(q)) * 120;
    ctx.globalAlpha = clamp(q * 3);
    ctx.fillStyle = C.cardShade; rr(-w / 2 + 40 + xo, yy, w - 80, 92, 46); ctx.fill();
    circle(-w / 2 + 92 + xo, yy + 46, 34, C.ink);
    disp('abcd'[i], -w / 2 + 92 + xo, yy + 42, 44, C.amber);
    disp(o, -w / 2 + 150 + xo, yy + 48, 46, C.ink, 'left', -1);
    ctx.globalAlpha = 1;
  });
  ctx.restore();
}
/** comment bubble prompt (flat), with a pencil-free "?" */
export function askBubble(x, y, s = 1, text = 'COMMENT a / b / c / d') {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const w = measure(text, 46, 'Mono', 700, 2) + 80, h = 100;
  ctx.fillStyle = C.amber; rr(-w / 2, -h / 2, w, h, 50); ctx.fill();
  ctx.beginPath(); ctx.moveTo(-w / 2 + 70, h / 2 - 4); ctx.lineTo(-w / 2 + 50, h / 2 + 34); ctx.lineTo(-w / 2 + 120, h / 2 - 4); ctx.fill();
  mono(text, 0, 2, 46, C.ink, 'center', 2);
  ctx.restore();
}
/** flat icon: judge's gavel (for courts / judges) */
export function gavel(x, y, s = 1, rot = -0.5) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = C.cardShade; rr(-150, 120, 300, 60, 14); ctx.fill();           // sound block
  ctx.rotate(rot);
  ctx.fillStyle = C.amber; rr(-18, -40, 36, 260, 14); ctx.fill();                 // handle
  ctx.fillStyle = C.card; rr(-110, -110, 220, 100, 24); ctx.fill();               // head
  ctx.fillStyle = C.cardShade; ctx.fillRect(-70, -110, 26, 100); ctx.fillRect(44, -110, 26, 100);
  ctx.restore();
}
/** flat icon: rupee coin stack with a downward coral arrow (a cut) */
export function coinCut(x, y, s = 1, p = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  for (let i = 0; i < 4; i++) { ctx.fillStyle = C.tealDark; rr(-110, 60 - i * 44 + 10, 220, 40, 20); ctx.fill(); ctx.fillStyle = C.teal; rr(-110, 60 - i * 44, 220, 40, 20); ctx.fill(); }
  circle(0, -150, 90, C.amber); disp('₹', 0, -146, 110, C.ink);
  const e = eo(clamp(p)); if (e > 0) {
    ctx.fillStyle = C.coral; ctx.beginPath(); const ay = lerp(-140, 0, e);
    ctx.moveTo(170, ay - 120); ctx.lineTo(210, ay - 120); ctx.lineTo(210, ay); ctx.lineTo(250, ay); ctx.lineTo(190, ay + 70); ctx.lineTo(130, ay); ctx.lineTo(170, ay); ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}
/** big counter: number + mono unit under it */
export function counter(value, unit, x, y, size = 360, color = C.white) {
  disp(String(value), x, y, size, color); mono(unit, x, y + size * 0.62, 56, C.slate, 'center', 8);
}
/** small mono header strip at the top band: e.g. "POLITY · EMERGENCY PROVISIONS" */
export function header(text, a = 1) {
  ctx.globalAlpha = a; mono(text, 540, 250, 38, C.slate, 'center', 5); ctx.fillStyle = C.teal; ctx.fillRect(480, 292, 120, 8); ctx.globalAlpha = 1;
}
