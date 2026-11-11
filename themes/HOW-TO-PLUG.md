# How to load a repo theme into the engine

The faceless-shorts skill folder may be read-only, so work on a writable copy:

```bash
SKILL=<faceless-shorts skill folder>
cp -r "$SKILL" ./engine                                   # writable engine
git clone -b themes https://github.com/Pramod2960/shorts-upload.git lab
NAME=clause-board
mkdir -p ./engine/styles/$NAME
cp -r ./engine/styles/inside-out/example ./engine/styles/$NAME/example     # tools/, captions.js, timing.js, Inter font
cp -r lab/themes/$NAME/kit/. ./engine/styles/$NAME/example/                # theme overrides: index.html, main.js, lib.js, kit.js, fonts
cp lab/themes/$NAME/STYLE.md lab/themes/$NAME/style-sheet.png ./engine/styles/$NAME/
cd ./engine/styles/$NAME/example
mv src/shots.sample.js src/shots.js; mv script.sample.json script.json     # the sample renders as-is
rm -f data/*.json data/*.wav
```
Then use it like any style: `bash ./engine/scripts/new_video.sh <name> <short-name>`, rewrite script.json + src/shots.js,
voice.py → words.py → `node tools/capture.mjs check|cues|sheet|video`, `tools/mix.py`.
Only themes marked `approved` in REGISTRY.md may be used for publishing.
