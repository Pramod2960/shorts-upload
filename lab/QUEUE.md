# Content Lab queue

Pramod's requested jobs. Each Content Lab run: if any item below is `pending`, do the TOP pending item as this run's
NEW THEME job (instead of choosing a job yourself), then set it to `done → themes/<name>/ (candidate)` with the date.
Still ONE job per run, full QA, sample render, `candidate` only.

## Source: nafay3d.com Style Library (added 2026-11-13, requested by Pramod in chat)

Pramod picked these 4 styles from https://nafay3d.com/#library and explicitly asked for them to be added as QuickInfo
themes. The site states its Style Library prompts are free to use for your own videos. Rules for adapting:
- Rebuild in OUR engine's style-folder format (start from the closest built-in / clause-board kit), in our own code.
  The reference sources can't be downloaded from the workspace (nafay3d.com is blocked by the network allowlist),
  so work from the spec below — it's enough.
- Give each theme a QuickInfo identity: our own name, a tweaked palette and type (stay close in feel, not a clone),
  QuickInfo PYQ chips + final PYQ card. No "Nafay" name, logo or watermark anywhere in the video.
- Narrated (Kokoro voice) like every QuickInfo Short; sync beats to the voice timeline.

### 1. Quiz Countdown → suggested name `pyq-countdown` — pending
- Best for: ANY subject — the whole Short is built around the PYQ (great for "guess before the timer ends" hooks).
- Look: bright orange (#ff7a1a) background with diagonal stripes; white rounded question card ("QUESTION 1 / 1" mono
  label on top); four answer pills with round A/B/C/D letter badges; white timer ring that drains around a big
  countdown number; reveal = right pill turns green (#2fb36b) with a check + confetti, others fade; ink #1b1b1b.
- Type: Archivo Black (headings), Inter 800 (body), JetBrains Mono 700 (labels/numbers).
- Motion: card pops in → answers slide in one by one → ring drains while the number counts down (tick each second,
  louder at the end) → buzzer at zero → green flash + confetti → one-line fact explains the answer.
- Sound: upbeat game-show pad with hats/kick, pop for the card, whoosh + tick per answer, fanfare + sparkle on reveal
  (keep music low under narration).
- QuickInfo flow: hook + teaching lines on striped bg with the card used as a "concept card" → PYQ-frequency chips
  → the real PYQ as the quiz card with countdown ("comment your answer before 0") → reveal can stay hidden or
  shown per the skill's ending rule; last line loops to the hook.

### 2. Timeline Rail → suggested name `year-rail` — pending
- Best for: modern history, freedom struggle, constitutional amendments, schemes/missions launch years, "firsts".
- Look: deep green page (#0f2a24); cream vertical rail (#e8dcc0) the camera scrolls down; glowing year nodes;
  cream event cards (#f3ead7) with a big gold (#e8b04b) year and a small icon drawn in code; running year
  odometer in a corner; muted text #3c4a44.
- Type: Archivo Black (titles), Space Grotesk 700 (years/odometer), Inter 600 (body).
- Motion: camera scrolls along the rail, nodes light up, odometer rolls fast to the next year, card drops in.
- Sound: warm pad with soft clock pulse, whoosh per scroll, fast ticks while the odometer rolls, thud + chime as
  each card lands, open chord for the takeaway.

### 3. Math Canvas → suggested name `quant-slate` — pending
- Best for: quant/aptitude shortcuts (SSC, banking, railways), economy maths (CAGR, compound interest, inflation),
  science formulas.
- Look: dark slate (#12141b); equation written term by term in italic serif, white ink; yellow (#ffd166) box +
  handwritten note on the key term; graph whose curve plots itself to scale with a glowing teal (#4fd1c5) dot and a
  live value; dashed grey (#6b7080) comparison line; mute #8a90a0.
- Type: Instrument Serif italic (equations), Space Grotesk 700 (numbers), JetBrains Mono 500 (axes), Caveat 700
  (handwritten notes).
- Motion: equation writes term by term → box + note on key term → curve plots with live value → gap vs comparison line.
- Sound: calm slow pad, chalky tick per term, marker sound for the box, pluck per plotted step (pitch climbs with the
  value), low hit for the gap, open chord at the end.

### 4. Myth or Fact → suggested name `myth-buster` — pending
- Best for: common exam misconceptions (science, geography, polity "which statement is correct"), current-affairs
  claims, statement-type PYQs.
- Look: pale grey (#eef1f4) background; white statement card with a big quote mark; a guess bar; rubber stamp slams
  down — red (#e03131) MYTH or green (#2f9e44) FACT — with distressed ink; then one line of proof with a check icon;
  yellow accent #f5b700; ink #111111; mute #5a6270.
- Type: Archivo Black (headings), Anton (stamp), Inter 800 (body).
- Motion: statement card in → guess bar fills → stamp slams (slight shake) → proof line pops in.
- Sound: light pad, pop + paper per card, soft ticks for the guess bar, heavy stamp + buzzer (myth) or ding (fact),
  pop for proof, open chord at the end.
