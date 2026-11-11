# Clause Board — QA notes

## 2026-11-11 (first build, sample "India's Emergency That Was Never Used", 20.9 s)
Caught and fixed during QA (3 rounds):
- Cards dealt from BELOW crossed the caption zone for ~0.2 s (5.75 s, 11.25 s) → deal now comes from the right edge.
- Top mono header sat at y 150 and got pushed off-frame by the camera punch-in → moved to y 250, band deepened.
- "NEVER USED" stamp overlapped the "TIMES PROCLAIMED" unit → stamp lowered to y 1090.
- Coral cut-arrow overlapped the gavel, then the gavel handle clipped the right edge → coin stack x 230, gavel x 730.
Open points for the next refine:
- PYQ card has a gap between the stem and the options when the stem is short; auto-place options under the last line.
- Sample runs 20.9 s (target 15-20) because the PYQ card needs ~2.4 s outro to be readable.
- Question text is 44 px; fine on a phone but long stems (> 6 lines) would need 40 px.
