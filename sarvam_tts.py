"""First Sarvam call: Hinglish text -> speech (Bulbul v3), saved as a WAV file.

Usage: python3 sarvam_tts.py ["text"] [out.wav] [speaker] [model]
Reads SARVAM_API_KEY from the environment, or from the .env file next to this script.
"""
import base64
import os
import sys
from pathlib import Path

from sarvamai import SarvamAI

env = Path(__file__).with_name(".env")
if "SARVAM_API_KEY" not in os.environ and env.exists():
    for line in env.read_text().splitlines():
        k, _, v = line.partition("=")
        if k.strip() and not line.lstrip().startswith("#"):
            os.environ.setdefault(k.strip(), v.strip())

text = sys.argv[1] if len(sys.argv) > 1 else (
    "क्या आपको पता है? ये question UPSC में तीन बार आ चुका है। "
    "PYQ Mitra dot com पर जाइए, और अपना government exam crack कीजिए!"
)
out = sys.argv[2] if len(sys.argv) > 2 else "sarvam_test.wav"
speaker = sys.argv[3] if len(sys.argv) > 3 else "shubh"
model = sys.argv[4] if len(sys.argv) > 4 else "bulbul:v3"

client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])
res = client.text_to_speech.convert(
    text=text,
    language_code="hi-IN",
    model=model,
    speaker=speaker,
)
Path(out).write_bytes(base64.b64decode("".join(res.audios)))
print(f"request_id: {res.request_id}")
print(f"saved: {out} ({Path(out).stat().st_size} bytes)")
