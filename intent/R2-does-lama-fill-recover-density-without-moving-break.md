# R2 — Does full-res LaMa fill recover sherd density without moving the break, with generated flagged in the PLY?

**Status:** open · **Blocked by:** none · **Effort:** days — one sherd, one seed, A/B on existing data

## Pin (2026-10-12, ticket 01 — verified before any job)

LaMa `https://github.com/advimman/lama` HEAD `786f5936b27fb3dacd2b1ad799e4de968ea697e7`; weights `big-lama` (`https://huggingface.co/smartywu/big-lama/resolve/main/big-lama.zip`). One sherd **A31** (33 views, 3200x2133); control `/data/gpfs/projects/punim2657/MILo/data/17062025/A03_sherds/` (164 views, `llffhold` 8). Both arms: 30k iters, seed 22, extraction voxel 0.002 = 0.75 mm, sdf_trunc 5×voxel, depth_trunc 5.0, 10 clusters. Env `/data/gpfs/projects/punim2657/MILo/envs/milo` + additive `albumentations`. Inpaint mask = complement of `A03_erode0` tight masks, 0 px dilation, per-view full-res, break and jaw-contact excluded. Face tolerance for ticket 02 (decided 2026-10-12 interview): **0.5 mm** on a quiet flat-wall patch, single representative A31 view first; deviation above this stops the trial and is recorded here with a date. Full record: `PGSR/.scratch/lama-face-fill/issues/01-pin-record.md`.

## Ticket 02 outcome (2026-10-13 — photo seam; conservator proceeded to clamp)

- Single-view gate on A31_1116: face-only 48px patch (cx1556 cy320, ≈10.57 mm side), pinned big-lama fill, lead-verified gray mean|Δ| 5.51 / rms 6.98 (N=2304 px), outside-box change 0, close-ups faithful (slightly softer, no invention). Full record: `PGSR/.scratch/lama-face-fill/issues/02-heldout-patch-check.md`; scorer `PGSR/scripts/measure_patch_deviation.py`; close-ups `PGSR/artifacts/lama02_eye/gate02_*`.
- Lead ruling: photo-gate PASSES fail-fast (no photographic stop signal); the photo-proxy "1.215 mm" (gray×mm/px) does NOT bind against the 0.5 mm surface tolerance — it measures no surface. No MISS recorded. Binding check of the same 0.5 mm moves to the fused-mesh scoring seam (tickets 03/04). No clamp pixels touched at gate time. Conservator eye note 2026-10-13: **proceed to clamp**.

## Where it stands

The fill software reproduced a hidden patch of plain pot wall faithfully at photo level — same tone and grain, slightly softer, nothing invented. The photo-level difference (about 5 brightness steps out of 255) cannot be read as millimetres of surface error: no 3-D surface exists at this stage to measure against. So this gate passes its narrow purpose (no photographic stop signal) without passing or failing the 0.5 mm surface limit — that check moves to the mesh stage, where the real surface gets measured. One pot, one patch, one run: a lead, not a conclusion. No clamp-area pixels touched.
Weight: one sherd (A31), one view, one 10.6 mm patch, one run.
Next: conservator eye note on the side-by-side close-ups, then mesh-seam instrument (tickets 03/04) for the binding 0.5 mm check.
Picture: PGSR/artifacts/lama02_eye/gate02_side_by_side.png | Held-out wall patch: true photo (left) vs LaMa fill (right), green box 48px = 10.6 mm side

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
