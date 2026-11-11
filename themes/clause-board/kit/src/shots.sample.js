// CLAUSE BOARD sample: "India's Emergency That Was Never Used" (Article 360). Shot list + sound cues.
// A shot: { id, at, cam: [cx, cy], zoom, note, draw(lt, d, t) }. Cut = L(i) - 0.08.
import { ctx, C, W, H, clamp, lerp, seg, eo, eio, eob, rnd } from './core/lib.js';
import { L, Le, Wd, T } from './core/timing.js';
import * as K from './core/kit.js';

export function buildShots() {
  const S = [], CUES = [];
  const add = (o) => (S.push(o), o);
  const cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);

  // ── 1a · HOOK: the EMERGENCY card is dealt onto the board ──────────────
  {
    const st = cut(0);
    add({ id: 'S01', at: st, cam: [540, 760], zoom: 0.08, note: 'emergency card dealt in, marker on EMERGENCY',
      draw(lt, d, t) {
        K.board(t); K.header('POLITY · THE CONSTITUTION', clamp(lt * 3));
        const c = K.deal(seg(lt, 0, 0.55), 540, 720, 1);
        ctx.save(); ctx.translate(c.x, c.y); ctx.rotate(c.rot);
        K.card(0, 0, 860, 620, 0, { tab: 'PART XVIII' });
        K.mono('THREE KINDS OF', -360, -170, 40, C.slate);
        K.marker(-372, -100, 700, 104, seg(lt, 0.7, 1.1));
        K.disp('EMERGENCY', -360, -46, 118, C.ink, 'left');
        ['NATIONAL · ART 352', 'STATE · ART 356', 'FINANCIAL · ART 360'].forEach((s, i) => {
          const q = seg(lt, 0.9 + i * 0.22, 1.2 + i * 0.22); ctx.globalAlpha = q;
          K.mono(s, -360 + (1 - eo(q)) * 60, 66 + i * 72, 44, i === 2 ? C.tealDark : C.ink); ctx.globalAlpha = 1;
        });
        ctx.restore();
      } });
    cue(st + 0.1, 'slide', { dur: 0.45, gain: 0.5 }); cue(st + 0.55, 'thud', { gain: 0.6 }); cue(st + 0.7, 'sparkle', { dur: 0.4, gain: 0.35 });
  }
  // ── 1b · NEVER USED stamp + zero counter ───────────────────────────────
  {
    const st = Wd('never', 0) - 0.12, slam = 0.12;
    add({ id: 'S02', at: st, cam: [540, 700], zoom: 0.1, note: 'counter 0 TIMES, coral NEVER USED stamp slams',
      draw(lt, d, t) {
        K.board(t); K.header('FINANCIAL EMERGENCY · SINCE 1950');
        K.counter('0', 'TIMES PROCLAIMED', 540, 640, 440);
        if (lt > slam) K.stamp('NEVER USED', 540, 1090, 96, -0.12, lerp(1.7, 1, eob(seg(lt, slam, slam + 0.22))));
      } });
    cue(st, 'whoosh'); cue(st + slam + 0.12, 'slam', { gain: 0.7 });
  }
  // ── 2 · ARTICLE 360 tab slams; FINANCIAL marked ────────────────────────
  {
    const st = cut(1), fin = Wd('financial', 1) - st;
    add({ id: 'S03', at: st, cam: [540, 760], zoom: 0.08, note: 'teal 360 tab slams, card FINANCIAL EMERGENCY with marker on "financial"',
      draw(lt, d, t) {
        K.board(t); K.header('THE CLAUSE');
        K.articleTab('360', 540, 560, lerp(1.6, 1, eob(seg(lt, 0.05, 0.3))));
        K.connector(540, 760, 540, 880, seg(lt, 0.5, 0.9));
        const c = K.deal(seg(lt, fin - 0.5, fin), 540, 1040, 4);
        ctx.save(); ctx.translate(c.x, c.y); ctx.rotate(c.rot);
        K.card(0, 0, 860, 300, 0, { ruled: false });
        K.marker(-340, -96, 560, 92, seg(lt, fin, fin + 0.4));
        K.disp('FINANCIAL', -330, -48, 96, C.ink, 'left');
        K.disp('EMERGENCY', -330, 62, 96, C.ink, 'left');
        ctx.restore();
      } });
    cue(st, 'whoosh'); cue(st + 0.2, 'slam', { gain: 0.5 }); cue(st + fin, 'slide', { dur: 0.4, gain: 0.4 });
  }
  // ── 3 · the President can cut even judges' salaries ────────────────────
  {
    const st = cut(2), cutW = Wd('cut', 2) - st, judg = Wd('judges', 2) - st;
    add({ id: 'S04', at: st, cam: [540, 720], zoom: 0.1, note: 'coin stack, coral arrow on "cut", gavel + JUDGES tag on "judges"',
      draw(lt, d, t) {
        K.board(t); K.header('ART 360(4)(b)');
        K.coinCut(230, 820, 1.35, seg(lt, cutW, cutW + 0.35));
        const g = seg(lt, judg - 0.3, judg + 0.1);
        if (g > 0) K.gavel(730, lerp(1250, 760, eob(g)), 1.35, lerp(-0.5, -0.9 + Math.sin(clamp(lt - judg) * 18) * 0.15 * (lt > judg ? 1 : 0), 1));
        if (lt > judg) K.chip('SC + HC', 'JUDGES', 540, 1110, 1.3 * lerp(0.6, 1, eob(seg(lt, judg, judg + 0.2))));
      } });
    cue(st, 'whoosh'); cue(st + cutW + 0.2, 'zip', { gain: 0.5 }); cue(st + judg + 0.05, 'thud', { gain: 0.7 });
  }
  // ── 4 · PYQ frequency chips (verified: UPSC Prelims 2007, UPSC Mains 2018) ──
  {
    const st = cut(3), pre = Wd('prelims', 3) - st, mai = Wd('mains', 3) - st;
    add({ id: 'S05', at: st, cam: [540, 760], zoom: 0.06, note: 'ASKED IN: ticket chips deal in on "prelims" and "mains", connector joins them',
      draw(lt, d, t) {
        K.board(t); K.header('ASKED IN');
        K.disp('UPSC', 540, 470, 200, C.white);
        const a = K.deal(seg(lt, pre - 0.15, pre + 0.3), 540, 720, 2), b = K.deal(seg(lt, mai - 0.15, mai + 0.3), 540, 1000, 5);
        K.connector(540, 790, 540, 930, seg(lt, mai - 0.3, mai));
        ctx.save(); ctx.translate(a.x, a.y); ctx.rotate(a.rot); K.chip('PRELIMS', '2007', 0, 0, 1.45); ctx.restore();
        ctx.save(); ctx.translate(b.x, b.y); ctx.rotate(b.rot); K.chip('MAINS GS-II', '2018', 0, 0, 1.45); ctx.restore();
      } });
    cue(st, 'whoosh'); cue(st + pre + 0.25, 'thud', { gain: 0.5 }); cue(st + mai + 0.25, 'thud', { gain: 0.5 });
  }
  // ── 5 · the PYQ card (UPSC Prelims 2007) + comment prompt ─────────────
  {
    const st = cut(4), com = Wd('comments', 4) - st;
    const Q = { exam: 'UPSC PRELIMS 2007', lines: ['*Financial Emergency (Art. 360):', '1. Ceases after two months unless', '    both Houses approve it.', "2. President may cut Union staff pay,", "    but NOT SC / HC judges' pay.", 'Which is / are correct?'],
      opts: ['1 only', '2 only', 'Both 1 and 2', 'Neither 1 nor 2'] };
    add({ id: 'S06', at: st, cam: [540, 700], zoom: 0.03, note: 'PYQ card dealt in, options slide in one by one, COMMENT bubble pops',
      draw(lt, d, t) {
        K.board(t);
        const c = K.deal(seg(lt, 0, 0.5), 540, 700, 7);
        K.pyqCard(c.x, c.y, Q, 1, [0, 1, 2, 3].map((i) => seg(lt, 0.6 + i * 0.18, 0.9 + i * 0.18)), c.rot);
        if (lt > com - 0.1) K.askBubble(540, 1290 + 330, lerp(0.5, 1, eob(seg(lt, com - 0.1, com + 0.15))));
      } });
    cue(st, 'whoosh'); [0, 1, 2, 3].forEach((i) => cue(st + 0.65 + i * 0.18, 'pop', { gain: 0.35 })); cue(st + com, 'pop', { gain: 0.6 });
  }
  return { shots: S, cues: CUES };
}
