# 10: Trace which prune rule kills the face cover during training

**What to build:** the open seam from ticket 07 — instrument ONE training run and watch the face-box cover die: which rule, at which iteration, under what stats. No fix in this ticket; the intervention is ticketed after, against the named rule.

**Answers:** R2

**Blocked by:** none (conservator chose trace-first 2026-10-15).

**Status:** in-progress
**Working in:** teammate t10-tracer, instrumented B_ctrl retrain (2026-10-15); named rule returns for lead ruling, fix is ticket 11 after

- [ ] Instrument the pinned trainer (COPY `scene/gaussian_model.py` + `train.py` densify/prune paths into ticket-local scripts — never edit the pinned files): per densify step in iters 500–15,000, log Gaussians inside the face box (centroid [-0.1812, 0.4883, -0.1933], half-edge 0.115 units) removed by EACH rule separately (opacity cull 0.005, post-3000 screen-size prune, observe<2 trim, opacity resets) with their grad/opacity/size stats at removal.
- [ ] Run ONE arm only: B_ctrl (starkest starvation — 0 cover at 30k; the prune code is shared, so the rule found applies to both). Same seed/config as ticket 03 (`train.py -s <arm> -m <out> -i images -r 1 --eval`, seed 22). ~2h45 GPU expected — batch job, polled, sacct recorded. Output to a ticket-local dir (never overwrite the ticket-03 scenes).
- [ ] Report: per-rule kill table over iteration (which rule takes how many face-box Gaussians when) + cover-vs-iter curve + pictured renders. Name the rule; do NOT change it here.
- [ ] Restraint: one arm, one run; no densification change, no LaMa-vs-control claim; small files to `artifacts/edge_10/`.

**Rules carried over:** worker appends work-notes only, never commits; GPU batch under standing sign-off with laptop-side poll; renders before numbers where load-bearing.
