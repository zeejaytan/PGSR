# R2 — Does full-res LaMa fill recover sherd density without moving the break, with generated flagged in the PLY?

**Status:** closed-uninformative · answered 2026-10-14 (see outcome below) · **Effort:** days — one sherd, one seed, A/B on existing data

## Pin (2026-10-12, ticket 01 — verified before any job)

LaMa `https://github.com/advimman/lama` HEAD `786f5936b27fb3dacd2b1ad799e4de968ea697e7`; weights `big-lama` (`https://huggingface.co/smartywu/big-lama/resolve/main/big-lama.zip`). One sherd **A31** (33 views, 3200x2133); control `/data/gpfs/projects/punim2657/MILo/data/17062025/A03_sherds/` (164 views, `llffhold` 8). Both arms: 30k iters, seed 22, extraction voxel 0.002 = 0.75 mm, sdf_trunc 5×voxel, depth_trunc 5.0, 10 clusters. Env `/data/gpfs/projects/punim2657/MILo/envs/milo` + additive `albumentations`. Inpaint mask = complement of `A03_erode0` tight masks, 0 px dilation, per-view full-res, break and jaw-contact excluded. Face tolerance for ticket 02 (decided 2026-10-12 interview): **0.5 mm** on a quiet flat-wall patch, single representative A31 view first; deviation above this stops the trial and is recorded here with a date. Full record: `PGSR/.scratch/lama-face-fill/issues/01-pin-record.md`.

## Ticket 02 outcome (2026-10-13 — photo seam; conservator proceeded to clamp)

- Single-view gate on A31_1116: face-only 48px patch (cx1556 cy320, ≈10.57 mm side), pinned big-lama fill, lead-verified gray mean|Δ| 5.51 / rms 6.98 (N=2304 px), outside-box change 0, close-ups faithful (slightly softer, no invention). Full record: `PGSR/.scratch/lama-face-fill/issues/02-heldout-patch-check.md`; scorer `PGSR/scripts/measure_patch_deviation.py`; close-ups `PGSR/artifacts/lama02_eye/gate02_*`.
- Lead ruling: photo-gate PASSES fail-fast (no photographic stop signal); the photo-proxy "1.215 mm" (gray×mm/px) does NOT bind against the 0.5 mm surface tolerance — it measures no surface. No MISS recorded. Binding check of the same 0.5 mm moves to the fused-mesh scoring seam (tickets 03/04). No clamp pixels touched at gate time. Conservator eye note 2026-10-13: **proceed to clamp**.

## Ticket 03/04 outcome (2026-10-14 — mesh seam; CAME BACK UNINFORMATIVE)

Both arms trained to 30k iters and fused cleanly at the stock grid, but neither arm yields a measurable sherd face: the cleanup pass deleted the sherd region from both meshes (hole at the sherd, worse in control), and the raw meshes hold only scattered fragments at the right place (mask-interior points land on the photographed face region yet form no surface in 3-D, faces/verts ~0.47 both arms, eye-confirmed). The scored boxes (break arc, wall noise, flag run) were REFUSED — numbers on fragments would be fabrication. The LaMa-vs-control question is unanswerable from this trial through no fault of either arm. Full record: `PGSR/.scratch/lama-face-fill/issues/03-training-ab-density.md`, `.../04-scoring-and-flag.md` (resolved honest-negative); evidence `PGSR/artifacts/edge_04c/` + `.../edge_04d/`.

## Where it stands

Came back uninformative (2026-10-14). The photo gate passed, but the mesh stage produced no surface to measure in either version — fragments sit where the face should be without forming one. So none of the Done-when boxes could be ticked, and none is claimed. This retires no option and funds nothing: LaMa is neither in the capture chain nor ruled out; the next attempt needs a finer grid or different surfacing first, on an object this small and partly hidden. One sherd, one seed, one grid: a stopped trial, not a verdict on the method.
Weight: one sherd (A31), one seed, both arms equally surfaceless at 0.75 mm grid.
Next: finer-grid or re-surfacing pilot IF the conservator wants one — ticketed separately, never folded silently into this A/B.

## Diagnosis update (2026-10-14, ticket 06 resolved)

Failure mechanism named with pictures: upstream Gaussian starvation — training deposits ~zero cover at the face (3σ: A 35, B 0 of ~650k), so fusion integrates clamp/background depth into ≤32-tri confetti. Grid (0.002) and keep-10 filter acquitted; occlusion starvation ruled out (19/28 views constrain). Retry direction, if ever funded: face-targeted densification + retrain (~2h45 GPU/arm), NOT finer voxels or looser filtering. Record: `PGSR/.scratch/lama-face-fill/issues/06-diagnose-sherd-fusion-failure.md`; evidence `PGSR/artifacts/edge_06/`.

## Reason update (2026-10-14, ticket 07 resolved)

One level deeper: seeds (6,593 at the face) and gradients (face bbox highest-energy in frame) both present — yet cover gone by iter 30k. The clearing happens DURING training (iters 500–15k) by an unidentified prune rule; needs training-time traces (possible future ticket). Author baseline: DTU object scans nearest (same mm ruler); no clamp-held small-face case in the paper — "same ruler, harder case," a domain gap, not a defect in our run. Record: `PGSR/.scratch/lama-face-fill/issues/07-why-starvation-author-baseline.md`; evidence `PGSR/artifacts/edge_07/`.
Picture: PGSR/artifacts/edge_04c/sidebyside_A31_1116.png | Fragments project onto the masked face region (LaMa left, control right) — right place
Picture: PGSR/artifacts/edge_04d/A_lama_A31_1116_tri_0.png | Same points as shaded 3-D surface — scattered slivers, no face

## Fill-baseline update (2026-10-14, ticket 08 resolved)

The LaMa fill itself, set against the authors' showing: mask shape inside demonstrated territory (ours relatively narrower), resolution beyond it (3200 vs ≤512 quant / 1536 curve / ~2k claim), content unrepresented (plain wall vs rooms/faces) — and the big-lama weights we run were never quantitatively covered at any size (base quant is LaMa-Fourier). Ticket 02's "faithful, slightly softer" stands as observed with no author-backed generality. Calibration (Places365 val + author narrow mask + pinned predict.py) proposed, uncleared — needs the conservator (external download). Record: `PGSR/.scratch/lama-face-fill/issues/08-lama-author-fill-baseline.md`; evidence `PGSR/artifacts/edge_08/`.

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
