# 04: Scoring — break stability, wall noise, flag-exclusion run

**What to build:** the detail half of R2 plus the honesty mechanism: proof the break did not move, the walls did not roughen, and the generated flag is actually honoured downstream.

**Answers:** R2

**Blocked by:** 03 (training A/B density figures) — extraction + first-look render done 2026-10-14; inputs ready.

**Lead note (read before starting):** 03's auto-crop close-ups missed the sherd (framed fusion-boundary tears at different spots per arm) — crop at the sherd's known 3D location from the photo masks/COLMAP frustums, and attach scale provenance (A03 373.733 mm/unit is assumed, unproven for A31) before any number counts. Gross fusion sanity confirmed; no face verdict stands yet.

**Status:** in-progress
**Working in:** teammate t04-scorer, phase 1 = sherd location + matching renders (2026-10-14); scoring/flag phase 2 follows lead inspection

- [ ] Break-face arc agreement A−B in mm of arc on 2–3 sampled edges, far below erosion width; any break move recorded as contamination
- [ ] Flat-wall noise A vs B as RMS residual in mm on quiet faces
- [ ] Generated-vs-measured flag written in the PLY and proven honoured by a matcher run that demonstrably excludes flagged vertices (colour alone does not count)
- [ ] Scale provenance attached (unscaled results refused, not measured); which of the three the outcome is named (method failed / measurement broken / reference wrong)
