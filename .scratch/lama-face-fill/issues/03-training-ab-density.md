# 03: Training A/B on inpainted vs control inputs, density figures

**What to build:** the two trainings that answer the density half of R2: arm A on LaMa-inpainted inputs (mask-free, production loss untouched), arm B the unmasked control — with density reported as counts, not impressions.

**Answers:** R2

**Blocked by:** 02 (held-out-patch check passed).

**Status:** ready-for-agent

- [ ] Both arms trained at full capture resolution, identical seed/config/iterations, every-8th-view holdout kept
- [ ] Gaussian counts A vs B, mesh vertex counts A vs B, kept-Gaussian footprint median/p90 in mm for both arms
- [ ] Laptop-side poll started on every submit; small renders/metrics in the landing zone, heavy data stays on the cluster
- [ ] No background-loss or pruning arm added (M5/M4 stay retired); the LaMa arm trains mask-free on filled inputs
