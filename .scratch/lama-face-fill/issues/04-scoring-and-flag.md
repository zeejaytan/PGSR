# 04: Scoring — break stability, wall noise, flag-exclusion run

**What to build:** the detail half of R2 plus the honesty mechanism: proof the break did not move, the walls did not roughen, and the generated flag is actually honoured downstream.

**Answers:** R2

**Blocked by:** 03 (training A/B density figures).

**Status:** ready-for-agent

- [ ] Break-face arc agreement A−B in mm of arc on 2–3 sampled edges, far below erosion width; any break move recorded as contamination
- [ ] Flat-wall noise A vs B as RMS residual in mm on quiet faces
- [ ] Generated-vs-measured flag written in the PLY and proven honoured by a matcher run that demonstrably excludes flagged vertices (colour alone does not count)
- [ ] Scale provenance attached (unscaled results refused, not measured); which of the three the outcome is named (method failed / measurement broken / reference wrong)
