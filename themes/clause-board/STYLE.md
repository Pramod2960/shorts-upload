# Clause Board — QuickInfo theme (candidate)

Flat index cards on a dark navy study board. Built for **polity, constitution articles, acts, constitutional/statutory
bodies, government schemes & reports** — topics that are really "a clause + a number + a condition", which Inside Out
(bodies/science) and Paper Atlas (maps/history) don't serve well.

## Look
- Board `#102033` with a slow-drifting dot grid (`#1C3352`) and a darker top band (`#0B1828`). No gradients, no glow.
- Ivory index cards `#F5F1E6` (one flat shade `#DCD5C3`, faint ruled lines `#C9C0AA`), flat drop in `#0B1828`.
- **Teal `#19B5A5` = the clause** (article tabs, card tabs, section labels).
- **Amber `#FFB627` = the key word** (marker swipe, caption keyword, PYQ year, comment bubble).
- **Coral `#F25C54` = never / limit / cut / exception** (rubber stamps, down arrows).
- Slate `#7A8BA6` for headers, units and dashed connectors. Ink `#0E1726` for text on cards.
- Type: Inter Black (headlines, numbers, captions) + bold mono (`fonts/DejaVuSansMono-Bold.ttf`, family `Mono`) for
  labels, headers, chips. Every shot has a small mono header at y 250 ("POLITY · THE CONSTITUTION", "ART 360(4)(b)").

## Signature motion
1. **Deal**: cards/chips slide in from the right edge with a small tilt and settle (`K.deal(p, x, y, k)`).
   From the side, never from below, so nothing crosses the caption zone (y 1250-1550).
2. **Slam**: article tabs and coral stamps scale 1.6 → 1 with overshoot on their word.
3. **Marker**: an amber swipe draws left-to-right under the keyword (`K.marker`).
4. **Connector**: a dashed slate line draws between two ideas (`K.connector`).

## PYQ
- Frequency line → one **ticket chip** per verified instance: `K.chip('PRELIMS', '2007', x, y, 1.45)` (mono exam on
  ivory | amber year on ink, ticket notches). Big white "UPSC"/"SSC" word above them. Chips = exactly the verified list.
- Final PYQ → `K.pyqCard(x, y, { exam, lines, opts }, 1, rowProgress[4], rot)`: teal exam tab, stem lines (prefix `*`
  for an amber-highlighted line), a/b/c/d pill rows sliding in one by one; then `K.askBubble()` ("COMMENT a / b / c / d")
  below the caption at y ~1620. Keep `outro` ≈ 2.4 s so the card stays readable.

## Kit (`kit/src/core/kit.js`)
`board(t)` · `header(text)` · `card(x,y,w,h,rot,{ruled,tab})` · `articleTab(num,x,y,s,label)` · `marker(x,y,w,h,p)` ·
`stamp(text,x,y,size,rot,sc)` · `connector(ax,ay,bx,by,p)` · `chip(exam,year,x,y,s)` · `pyqCard(...)` · `askBubble(x,y,s)` ·
`counter(value,unit,x,y,size)` · `gavel(x,y,s,rot)` · `coinCut(x,y,s,p)` · text helpers `disp()`, `mono()`, `measure()`.
New topic → add flat icons in the same palette (one flat darker shade, no outlines on icons).

## Shot pattern (sample, 21 s, Article 360)
hook card (Part XVIII, three emergencies) → "0 TIMES PROCLAIMED" + NEVER USED stamp → ARTICLE 360 tab + marked card →
icons for the key provision → ASKED IN chips → PYQ card + comment bubble. Sound: whoosh every cut, thud on deal,
slam on stamps/tabs, soft pops for option rows. Music `bed`, voice am_michael x1.1.
