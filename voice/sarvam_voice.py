"""Hinglish narration for a faceless-shorts project: Sarvam Bulbul v3 (speaker shubh), else free Kokoro as fallback.

  python3 sarvam_voice.py <project>              script.json -> data/narration.wav + data/lines.json (same as engine voice.py)
  python3 sarvam_voice.py <project> --kokoro     skip Sarvam, force the Kokoro fallback (to test it)

Each script.json line has "text" (Roman Hinglish: captions + word timing) and "say" (what is spoken, e.g. Devanagari
with English words, "ये question UPSC में ..."). Without "say", "text" is spoken.
Sarvam is used when SARVAM_API_KEY is set (env or the .env next to this file) and the calls succeed. On ANY Sarvam error
(no credits = 402, network, bad key) the whole narration is redone with Kokoro (voice "fallback_voice", default
hm_omega, Hindi), so one video never mixes two voices. Run with the engine's python (scripts/py) for Kokoro.
"""
import argparse, base64, io, json, os, re, sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

SR = 24000
HERE = Path(__file__).resolve().parent
USAGE = {'chars': 0}  # characters sent to Sarvam in this run (also counted when a later call fails)


def trim(x, thr=0.008):
    idx = np.where(np.abs(x) > thr)[0] if len(x) else []
    if not len(idx): return x
    return x[max(0, idx[0] - int(0.01 * SR)):min(len(x), idx[-1] + int(0.03 * SR))]


def silences(x, thr=0.012, min_len=0.06):
    hop = int(0.01 * SR); n = len(x) // hop
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)); quiet = rms < thr * np.abs(x).max()
    out, st = [], None
    for f, q in enumerate(quiet):
        if q and st is None: st = f
        if (not q or f == n - 1) and st is not None:
            if (f - st) * 0.01 >= min_len: out.append((st * 0.01, f * 0.01))
            st = None
    return out


def sarvam_say(S):
    if 'SARVAM_API_KEY' not in os.environ and (HERE / '.env').exists():
        for ln in (HERE / '.env').read_text().splitlines():
            k, _, v = ln.partition('=')
            if k.strip() and not ln.lstrip().startswith('#'): os.environ.setdefault(k.strip(), v.strip())
    key = os.environ.get('SARVAM_API_KEY')
    if not key: raise RuntimeError('SARVAM_API_KEY not set')
    from sarvamai import SarvamAI
    client = SarvamAI(api_subscription_key=key)
    model, speaker, pace = S.get('sarvam_model', 'bulbul:v3'), S.get('sarvam_speaker', 'shubh'), S.get('sarvam_pace', 1.0)

    def say(text):
        USAGE['chars'] += len(text)  # Sarvam bills per character sent (v3: Rs 3 per 1,000)
        r = client.text_to_speech.convert(text=text, language_code='hi-IN', model=model, speaker=speaker,
                                          pace=pace, speech_sample_rate=SR, output_audio_codec='wav')
        sr, raw = wavfile.read(io.BytesIO(base64.b64decode(''.join(r.audios))))
        y = raw.astype(np.float64) / (32768 if np.issubdtype(raw.dtype, np.integer) else 1)
        y = y.mean(axis=1) if y.ndim > 1 else y
        if sr != SR: y = resample_poly(y, SR, sr)
        return trim(y)
    return say, f'sarvam:{model}:{speaker}'


def kokoro_say(S):
    from kokoro_onnx import Kokoro
    kd = Path(os.environ.get('FACELESS_HOME', Path.home() / '.faceless-shorts')) / 'kokoro'
    k = Kokoro(str(kd / 'kokoro-v1.0.onnx'), str(kd / 'voices-v1.0.bin'))
    voice = S.get('fallback_voice', 'hm_omega'); speed = S.get('speed', 1.0)
    lang = 'hi' if voice.startswith('h') else ('en-gb' if voice.startswith('b') else 'en-us')
    return (lambda text: trim(np.asarray(k.create(text, voice=voice, speed=speed, lang=lang)[0], dtype=np.float64))), f'kokoro:{voice}'


def build(S, say):
    L = S['lines']; spoken = lambda i: L[i].get('say', L[i]['text'])
    groups, cur = [], []
    for i, ln in enumerate(L):
        cur.append(i)
        if re.search(r'[.?!।]["\')]*$', spoken(i).strip()) or ln.get('break') or i == len(L) - 1: groups.append(cur); cur = []
    out = [np.zeros(int(S.get('lead', 0.4) * SR))]; t = len(out[0]) / SR; lines = [None] * len(L)
    for g in groups:
        x = say(' '.join(spoken(i) for i in g)); n = len(x) / SR; cuts = [0.0]
        if len(g) > 1:  # cut points: split by spoken length, snapped to the nearest pause
            lens = np.array([len(spoken(i)) for i in g], dtype=float); pauses = silences(x)
            for c in np.cumsum(lens)[:-1] / lens.sum() * n:
                near = [p for p in pauses if abs((p[0] + p[1]) / 2 - c) < 0.5]
                p = min(near, key=lambda p: abs((p[0] + p[1]) / 2 - c)) if near else (c, c); cuts.append(p)
        for j, i in enumerate(g):
            a = 0.0 if j == 0 else cuts[j][1]; b = n if j == len(g) - 1 else cuts[j + 1][0]
            lines[i] = {'i': i, 'text': L[i]['text'], 'start': round(t + a, 3), 'end': round(t + b, 3)}
            print(f'{i:2d} {lines[i]["start"]:6.2f}-{lines[i]["end"]:6.2f}  {L[i]["text"]}', flush=True)
        gap = np.zeros(int(float(L[g[-1]].get('gap', S.get('gap', 0.3))) * SR))
        out += [x, gap]; t += (len(x) + len(gap)) / SR
    out.append(np.zeros(int(float(S.get('outro', 0.9)) * SR)))
    y = np.concatenate(out); return y / (np.abs(y).max() + 1e-9) * 0.9, lines


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--kokoro', action='store_true')
    a = ap.parse_args(); P = Path(a.project); S = json.loads((P / 'script.json').read_text())
    y = None
    if not a.kokoro:
        try:
            say, voice = sarvam_say(S); y, lines = build(S, say)
        except Exception as e:  # no credits (402), network, key... -> free fallback for the WHOLE narration
            code = getattr(e, 'status_code', None); body = getattr(e, 'body', None) or str(e)
            msg = re.sub(r'sk_\w+', 'sk_***', str(body))[:200]
            print(f'Sarvam failed ({type(e).__name__} {code or ""}: {msg}); falling back to Kokoro', file=sys.stderr)
    if y is None:
        say, voice = kokoro_say(S); y, lines = build(S, say)
    (P / 'data').mkdir(exist_ok=True)
    wavfile.write(P / 'data/narration.wav', SR, (y * 32767).astype(np.int16))
    dur = len(y) / SR
    (P / 'data/lines.json').write_text(json.dumps({'duration': round(dur, 3), 'voice': voice, 'speed': S.get('sarvam_pace', 1.0),
                                                   'sarvam_chars': USAGE['chars'], 'lines': lines}, indent=1))
    print(f'data/narration.wav ({dur:.2f} s, {voice}) + data/lines.json. Next: words.py')
    print(f'sarvam_chars: {USAGE["chars"]} (~Rs {USAGE["chars"] * 3 / 1000:.2f} at bulbul:v3 rates)')


if __name__ == '__main__':
    main()
