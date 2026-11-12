# Hinglish voice (Sarvam Bulbul v3, Kokoro fallback)

Added 2026-11-12, decided by Pramod: every Short is narrated in Hinglish with Sarvam AI TTS
(`bulbul:v3`, speaker `shubh`). If Sarvam fails for any reason (credits over = HTTP 402, host
blocked, bad key), `sarvam_voice.py` redoes the WHOLE narration with the free Kokoro voice
(`hm_omega`, Hindi), so a video never mixes two voices.

Use it in place of the engine's `voice.py` (run with the engine's python so Kokoro is available):

    uv pip install --python ~/.faceless-shorts/venv/bin/python sarvamai
    SARVAM_API_KEY=proxy-injected SKILL/scripts/py voice/sarvam_voice.py <project>
    SKILL/scripts/py SKILL/scripts/words.py <project>

The real key is a network secret on the cloud environment (host api.sarvam.ai, header
`api-subscription-key`); the proxy swaps the placeholder for it. Never commit a key.

script.json extras: `"sarvam_model": "bulbul:v3"`, `"sarvam_speaker": "shubh"`, `"sarvam_pace": 1.1`,
`"fallback_voice": "hm_omega"`. Each line: `text` = Roman Hinglish (captions + word timing),
`say` = what is spoken (Devanagari with English words in Latin, e.g. "ये question UPSC में तीन बार आया है।"),
`caps` = Roman Hinglish caption chunks, one `*` yellow word each.
data/lines.json has "voice" (sarvam:... or kokoro:...) and "sarvam_chars" (characters billed this run; bulbul:v3 = Rs 3 per 1,000). There is no balance API: the dashboard (indus.sarvam.ai, Settings -> Billing) is the only exact source.
