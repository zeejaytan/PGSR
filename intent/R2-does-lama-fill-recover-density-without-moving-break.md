# R2 — Does full-res LaMa fill recover sherd density without moving the break, with generated flagged in the PLY?

**Status:** open · **Blocked by:** none · **Effort:** days — one sherd, one seed, A/B on existing data

## Why it matters

Masked training drains the clay (M5: 222,678 → 18,443 Gaussians, 2.6M → 276k verts) and fusion-time masking lands on a 0.75 mm grid (M8). The clamp covers face only, never the break, so a face fill cannot fake a join — but the open question is whether feeding LaMa-inpainted face pixels recovers density as clay or as smooth fake, and whether the break stays untouched. This decides if LaMa earns a place in the capture chain or stays a visualisation aid. GScream/InFusion are recorded backups, untested.

## Done when

- [ ] LaMa build **pinned by commit hash in this file before any job**; run on one sherd (same views/seed for both arms): (A) LaMa-inpainted training inputs vs (B) unmasked control
- [ ] Density recovery stated as counts: Gaussians A vs B, mesh verts A vs B, kept-Gaussian footprint median/p90 in **mm**
- [ ] Break-face arc agreement A−B in **mm of arc** on 2–3 sampled edges — must be ≪ erosion width; any break move is contamination, not success
- [ ] Flat-wall noise A vs B as RMS residual in **mm** on quiet faces; held-out known face patch deviation in **mm**
- [ ] Generated-vs-measured flag in the PLY that downstream matching actually ignores (colour alone does not count), demonstrated by feeding the flagged mesh to the matcher
- [ ] Rim/face close-up renders A vs B at a view resolving **~0.2 mm ridges**, witnessed by the conservator

## Gate / stop condition

- Break moves or wall noise rises clearly above control → retire NO; LaMa stays visualisation-only, GScream/InFusion stay parked.
- Density recovers but renders read as smooth fake on the fill → retire NO at one-sherd weight; do not fund a second seed.
- Density recovers as clay with break untouched and flag honoured → keep, and only then scope the second sherd and the GScream/InFusion comparison.
- Training-time taint rule: pixels grown from fake texture are inferred everywhere they constrain — if the flag cannot be honoured downstream, the dense mesh is not a record mesh regardless of counts.

## Source

User proposal 2026-10-05 (LaMa trial, GScream/InFusion as candidates; issue is general coarseness, not just clamp); M5 verdict 2026-09-06 (density collapse); M8 verdict 2026-09-13 (grid ceiling); U14 (labelled completion); R1 control figures (PGSR-A 96,719 verts, 0.77 mm median edge).
