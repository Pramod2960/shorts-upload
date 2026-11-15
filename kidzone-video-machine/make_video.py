"""KidZone Video Machine.

Turns a story text file into a finished kids' story video:
  story.txt -> Hindi voiceover (edge-tts) -> one image per scene with a slow
  zoom -> karaoke-style word captions -> background music -> MP4.

Usage (Windows, from this folder):
  python make_video.py stories\\khargosh-aur-kachhua.txt
  python make_video.py stories\\khargosh-aur-kachhua.txt --format short
  python make_video.py stories\\my-story.txt --voice hi-IN-MadhurNeural --music music\\happy.mp3

Workflow:
  1. First run writes output\\<story>\\prompts.txt and renders a preview with
     coloured placeholder images.
  2. Generate one image per prompt (Gemini / ChatGPT / local Stable Diffusion),
     save them as output\\<story>\\images\\01.png, 02.png, ...
  3. Run again. Voice is cached, so only the video is rebuilt.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent

FORMATS = {
    # name: (width, height, caption font size, caption bottom margin, words per caption line)
    "long": (1920, 1080, 78, 70, 5),
    "short": (1080, 1920, 96, 520, 3),
}
FPS = 30
SCENE_GAP = 0.45  # silence after each scene, seconds
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
PLACEHOLDER_COLORS = ["0x4FC3F7", "0x81C784", "0xFFB74D", "0xBA68C8", "0xF06292", "0x4DB6AC"]
STYLE_SUFFIX = (
    "Bright glossy 3D cartoon style for a children's story, cute friendly characters with big "
    "shiny eyes, soft warm lighting, vivid cheerful colors, simple clean background, "
    "child-friendly, nothing scary, no text in the image"
)


# ---------------------------------------------------------------- story file


@dataclass
class Scene:
    narration: str
    image_prompt: str = ""


@dataclass
class Story:
    title: str = ""
    meta: dict = field(default_factory=dict)
    scenes: list[Scene] = field(default_factory=list)


HEADER_KEYS = {"title", "format", "voice", "rate", "pitch", "music"}


def parse_story(path: Path) -> Story:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    lines = [ln for ln in text.split("\n") if not ln.lstrip().startswith("#")]
    blocks = [b.strip() for b in re.split(r"\n\s*\n", "\n".join(lines)) if b.strip()]
    story = Story()
    for block in blocks:
        rows = [r.strip() for r in block.split("\n") if r.strip()]
        header = [re.match(r"^([A-Za-z]+)\s*:\s*(.*)$", r) for r in rows]
        if all(m and m.group(1).lower() in HEADER_KEYS for m in header):
            for m in header:
                story.meta[m.group(1).lower()] = m.group(2).strip()
            continue
        prompt, words = "", []
        for r in rows:
            m = re.match(r"^(img|image)\s*:\s*(.*)$", r, re.IGNORECASE)
            if m:
                prompt = m.group(2).strip()
            else:
                words.append(r)
        if words:
            story.scenes.append(Scene(" ".join(words), prompt))
    story.title = story.meta.get("title", path.stem)
    if not story.scenes:
        sys.exit(f"No scenes found in {path}. Separate scenes with a blank line.")
    return story


# ---------------------------------------------------------------- helpers


def run(cmd: list[str], cwd: Path | None = None) -> None:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr[-3000:])
        sys.exit(f"\nffmpeg failed: {' '.join(cmd[:6])} ...")


def media_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def check_tools() -> None:
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing:
        sys.exit(
            "ffmpeg is not installed. On Windows run:  winget install Gyan.FFmpeg\n"
            "then close and reopen the terminal."
        )


# ---------------------------------------------------------------- voice


def tts_edge(text: str, voice: str, rate: str, pitch: str, mp3: Path) -> list[dict]:
    try:
        import edge_tts
    except ImportError:
        sys.exit("edge-tts is missing. Run:  pip install -r requirements.txt")

    async def go() -> list[dict]:
        comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
        words = []
        with open(mp3, "wb") as f:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start = chunk["offset"] / 1e7
                    words.append({"w": chunk["text"], "s": start, "e": start + chunk["duration"] / 1e7})
        return words

    return asyncio.run(go())


def tts_silent(text: str, mp3: Path) -> list[dict]:
    """Test backend: silent audio sized to the text, no internet needed."""
    dur = max(1.5, len(text) * 0.065)
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", f"{dur:.2f}",
         "-c:a", "libmp3lame", "-q:a", "4", str(mp3)])
    return []


def spread_words(text: str, duration: float) -> list[dict]:
    """Fallback timing: share the audio time between words by their length."""
    words = text.split()
    total = sum(len(w) + 2 for w in words)
    t, out = 0.15, []
    usable = max(0.5, duration - 0.3)
    for w in words:
        d = usable * (len(w) + 2) / total
        out.append({"w": w, "s": t, "e": t + d})
        t += d
    return out


def make_voice(scene: Scene, idx: int, audio_dir: Path, args) -> tuple[Path, list[dict], float]:
    mp3 = audio_dir / f"{idx:02d}.mp3"
    meta = audio_dir / f"{idx:02d}.json"
    key = hashlib.sha1(f"{args.tts}|{args.voice}|{args.rate}|{args.pitch}|{scene.narration}".encode()).hexdigest()
    if mp3.exists() and meta.exists():
        cached = json.loads(meta.read_text(encoding="utf-8"))
        if cached.get("key") == key:
            return mp3, cached["words"], cached["duration"]
    print(f"  voice  scene {idx:02d}")
    if args.tts == "silent":
        words = tts_silent(scene.narration, mp3)
    else:
        words = tts_edge(scene.narration, args.voice, args.rate, args.pitch, mp3)
    duration = media_duration(mp3)
    if not words:
        words = spread_words(scene.narration, duration)
    meta.write_text(json.dumps({"key": key, "duration": duration, "words": words}, ensure_ascii=False), encoding="utf-8")
    return mp3, words, duration


# ---------------------------------------------------------------- captions


def ass_time(t: float) -> str:
    cs = int(round(max(0.0, t) * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_escape(s: str) -> str:
    return s.replace("\\", "").replace("{", "(").replace("}", ")")


def write_captions(all_words: list[dict], out: Path, fmt: str, font: str) -> None:
    w, h, size, margin, per_line = FORMATS[fmt]
    # Colours are &HAABBGGRR. Spoken words turn yellow, upcoming words are white.
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kid,{font},{size},&H0000E5FF,&H00FFFFFF,&H00301A0A,&H96000000,1,0,0,0,100,100,0,0,1,7,3,2,60,60,{margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for i in range(0, len(all_words), per_line):
        group = all_words[i:i + per_line]
        start = group[0]["s"]
        end = group[-1]["e"] + 0.15
        nxt = all_words[i + per_line]["s"] if i + per_line < len(all_words) else None
        if nxt is not None:
            end = min(end, nxt)
        parts, t = [], start
        for wd in group:
            k = max(1, int(round((wd["e"] - t) * 100)))
            parts.append(f"{{\\kf{k}}}{ass_escape(wd['w'])}")
            t = wd["e"]
        events.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Kid,,0,0,0,,{' '.join(parts)}")
    out.write_text(head + "\n".join(events) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- video


def find_image(img_dir: Path, idx: int) -> Path | None:
    for name in (f"{idx:02d}", str(idx)):
        for ext in IMAGE_EXTS:
            p = img_dir / f"{name}{ext}"
            if p.exists():
                return p
    return None


def render_scene(idx: int, image: Path | None, mp3: Path, dur: float, out: Path, fmt: str, encoder: list[str]) -> None:
    w, h = FORMATS[fmt][:2]
    frames = max(1, int(round(dur * FPS)))
    zoom_in = idx % 2 == 1
    z = f"1+0.10*on/{frames}" if zoom_in else f"1.10-0.10*on/{frames}"
    fade_out = max(0.0, dur - 0.35)
    if image is not None:
        src = ["-i", str(image)]
        vf = (
            f"[0:v]scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
            f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={FPS},"
        )
    else:
        color = PLACEHOLDER_COLORS[(idx - 1) % len(PLACEHOLDER_COLORS)]
        src = ["-f", "lavfi", "-i", f"color=c={color}:s={w}x{h}:r={FPS}:d={dur:.3f}"]
        vf = "[0:v]"
    vf += f"fade=t=in:st=0:d=0.3,fade=t=out:st={fade_out:.3f}:d=0.35,format=yuv420p,setsar=1[v]"
    af = f"[1:a]aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur={dur:.3f}[a]"
    run(["ffmpeg", "-y", *src, "-i", str(mp3), "-filter_complex", f"{vf};{af}",
         "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}", "-r", str(FPS),
         *encoder, "-c:a", "aac", "-b:a", "192k", str(out)])


def write_prompts(story: Story, out: Path, fmt: str) -> None:
    ratio = "16:9 wide landscape" if fmt == "long" else "9:16 vertical portrait"
    lines = [f"Image prompts for: {story.title}",
             f"Save each image as images\\01.png, images\\02.png ... ({ratio}).",
             "Use the same character reference image every time so the characters look the same.", ""]
    for i, sc in enumerate(story.scenes, 1):
        base = sc.image_prompt or f"A scene from a children's story: {sc.narration}"
        lines.append(f"{i:02d}. {base}. {STYLE_SUFFIX}, {ratio} aspect ratio.")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


def build(args) -> Path:
    story_path = Path(args.story).resolve()
    story = parse_story(story_path)
    fmt = args.format or story.meta.get("format", "long")
    if fmt not in FORMATS:
        sys.exit("format must be 'long' or 'short'")
    args.voice = args.voice or story.meta.get("voice", "hi-IN-SwaraNeural")
    args.rate = args.rate or story.meta.get("rate", "-5%")
    args.pitch = args.pitch or story.meta.get("pitch", "+0Hz")
    music = args.music or story.meta.get("music")
    font = args.font or ("Nirmala UI" if platform.system() == "Windows" else "Noto Sans Devanagari")

    work = HERE / "output" / story_path.stem
    audio_dir, img_dir, clip_dir = work / "audio", work / "images", work / "clips"
    for d in (audio_dir, img_dir, clip_dir):
        d.mkdir(parents=True, exist_ok=True)
    write_prompts(story, work / "prompts.txt", fmt)

    encoder = (["-c:v", "h264_nvenc", "-preset", "p5", "-cq", "21"] if args.gpu
               else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"])

    print(f"Story: {story.title}  |  {len(story.scenes)} scenes  |  {fmt}  |  voice {args.voice}")
    all_words, clips, t0, missing = [], [], 0.0, []
    for i, sc in enumerate(story.scenes, 1):
        mp3, words, adur = make_voice(sc, i, audio_dir, args)
        dur = adur + SCENE_GAP
        image = find_image(img_dir, i)
        if image is None:
            missing.append(i)
        clip = clip_dir / f"{i:02d}.mp4"
        print(f"  video  scene {i:02d}  {dur:5.1f}s  {'image ' + image.name if image else 'placeholder'}")
        render_scene(i, image, mp3, dur, clip, fmt, encoder)
        clips.append(clip)
        all_words += [{"w": wd["w"], "s": wd["s"] + t0, "e": wd["e"] + t0} for wd in words]
        t0 += media_duration(clip)

    (work / "concat.txt").write_text("".join(f"file 'clips/{c.name}'\n" for c in clips), encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy", "joined.mp4"], cwd=work)

    write_captions(all_words, work / "captions.ass", fmt, font)
    fonts_dir = HERE / "fonts"
    sub = "subtitles=captions.ass" + (f":fontsdir='{os.path.relpath(fonts_dir, work).replace(os.sep, '/')}'"
                                      if fonts_dir.is_dir() and any(fonts_dir.iterdir()) else "")
    final = work / f"{story_path.stem}.mp4"
    cmd = ["ffmpeg", "-y", "-i", "joined.mp4"]
    if music:
        music_path = Path(music)
        if not music_path.is_absolute():
            music_path = (HERE / music_path) if (HERE / music_path).exists() else (story_path.parent / music_path)
        if not music_path.exists():
            sys.exit(f"Music file not found: {music}")
        cmd += ["-stream_loop", "-1", "-i", str(music_path),
                "-filter_complex",
                f"[0:v]{sub}[v];[1:a]volume={args.music_volume}[m];"
                "[0:a][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]",
                "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-vf", sub, "-c:a", "copy"]
    cmd += [*encoder, "-movflags", "+faststart"]
    if music:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    cmd += [final.name]
    print("  final  captions" + (" + music" if music else ""))
    run(cmd, cwd=work)

    print(f"\nDone: {final}  ({media_duration(final):.0f} seconds)")
    if missing:
        print(f"Placeholder colours used for scenes {', '.join(f'{m:02d}' for m in missing)}.")
        print(f"Image prompts: {work / 'prompts.txt'}")
        print(f"Put images in: {img_dir}  (01.png, 02.png ...) and run again.")
    return final


def main() -> None:
    p = argparse.ArgumentParser(description="KidZone Video Machine: story.txt -> MP4")
    p.add_argument("story", help="story text file, e.g. stories\\khargosh-aur-kachhua.txt")
    p.add_argument("--format", choices=sorted(FORMATS), help="long = 16:9 YouTube video, short = 9:16 Short")
    p.add_argument("--voice", help="edge-tts voice, e.g. hi-IN-SwaraNeural (female) or hi-IN-MadhurNeural (male)")
    p.add_argument("--rate", help="speaking speed, e.g. -10%% (slower) or +5%%")
    p.add_argument("--pitch", help="voice pitch, e.g. +10Hz for a brighter voice")
    p.add_argument("--music", help="background music file (mp3)")
    p.add_argument("--music-volume", default="0.10", help="background music volume, default 0.10")
    p.add_argument("--font", help="caption font name (default: Nirmala UI on Windows)")
    p.add_argument("--gpu", action="store_true", help="encode with the NVIDIA GPU (faster)")
    p.add_argument("--tts", choices=["edge", "silent"], default="edge", help="'silent' = test without internet")
    args = p.parse_args()
    check_tools()
    build(args)


if __name__ == "__main__":
    main()
