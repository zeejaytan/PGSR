# R1 — Does QGS preserve break-face edges beyond PGSR under PGSR-identical conditions?

**Status:** open · **Blocked by:** none (M8 answered NO as mesh route 2026-09-13; this is the follow-on) · **Effort:** days, not weeks — one capture, one seed

## Why it matters

PGSR is closed as a sherd mesh route (M8 verdict 2026-09-13: regs catch-22, 0.75 mm grid, variant B OOM ceiling — method failed on this material, type 1). A further Gaussian-splatting variant only earns GPU if it tests the one thing that could distinguish it: edge preservation on the break face itself. Anything else re-buys the ceiling M8 already measured. The decision this settles is narrow: fund one small PGSR-controlled A/B, or stop spending mesh-route GPU after PGSR.

Opinion before acting (workspace rule — researched, then stated): worth doing in general, not yet shown worth doing **for this**. QGS's distinguishing mechanism is exactly the right one to test — paraboloid primitives with geodesic density plus curvature-guided normal consistency (λK downweights the planar-assumption loss in high-curvature edge regions where 2DGS over-smooths; paper Fig. 2, Eq. 17, ablation "disabling curvature guidance fills fine gaps"). But its accuracy is shown only on clean benchmark objects at cm scale (DTU CD 0.54 vs PGSR 0.56, TNT F1 0.50) with no clamp rig and no 0.2 mm ridge bar; it fuses via the same Open3D TSDF class that hit the block/OOM ceiling in M8, carries the same PGSR-style multi-view homography+NCC regularization that fought chrome highlights in the regs catch-22, ships with no mask path, and its own authors report overfitting in sparse/low-texture regions with curvature losses unsatisfactory. Small-object accuracy at sherd scale with rig present is unmeasured — the trial's own edge boxes decide.

If QGS later earns its own sibling folder (same shape as this one — own remotes, own Slurm, heavy data on cluster), this question moves there by amendment, never by duplication. Number stays R1.

## Done when

- [ ] QGS build **pinned by commit hash in this file before any job**, trained on the existing `A03_sherds` dataset at full capture resolution (no silent downsample) — same 164 views M8 used
- [ ] Extraction at the **same voxel size and truncation band in millimetres** as the M8 verdict (0.75 mm grid stated with route sidecar), same fusion-time masks (variant-A community alpha construction); training-time masking and post-training pruning stay retired per M4/M5 without fresh justification
- [ ] Control is the **PGSR variant-A mesh from M8**, not OpenMVS — the question is "better than PGSR on edges", not "better than photogrammetry in general"
- [ ] Scored on **break-face relief specifically** (glossary sense: Ra/Rq height in mm after the break's own meander is filtered out, with cutoff stated) — fraction of break-face ribbon within the M1 ~1 mm requirement, not whole-sherd averages that dilute the edge
- [ ] Break-face close-up renders, QGS versus PGSR variant A, at a view that resolves **~0.2 mm ridges** — whole-sherd views have misled here repeatedly and tick no box
- [ ] Scale sidecar per M3 (refuse-not-measure on missing units) and rig check: remaining steel surface area in **cm²** on each extracted mesh

## Gate / stop condition

- Beats PGSR on edges **but lands on the same ceiling** (grid-limited relief, same ~1 mm / 0.2 mm bar missed): that's motion without progress per M8's own rule — retire NO at one-capture weight, do not fund a second seed or capture.
- Matches or beats PGSR on edges **and** clears a bar PGSR missed (parity-plus on the ~1 mm relief with ridge-resolving renders, or complementary honest coverage): keep, and only then scope the second capture.
- Hits the same extraction ceiling (Open3D block/OOM class): this becomes the tiling question — amend, do not build around it silently.
- A NO here costs days. Second seeds, second captures, re-photography, and viewing-only scoring are out of scope unless the base A/B passes.

## Source

QGS identified 2026-09-13: Quadratic Gaussian Splatting, ICCV '25 (CAS/HKU/SenseTime), repo `will-zzy/QGS`, paper arXiv:2411.16392 (quadric paraboloid primitives, geodesic density, ray-quadric intersection, curvature-guided normal consistency §3.3, Open3D TSDF fusion §4.1, DTU/TNT/MipNeRF360 only). User proposal 2026-09-13 (QGS trial only earns GPU as edge-preservation test under PGSR-identical conditions; PGSR mesh as control; same-ceiling = motion without progress); M8 verdict 2026-09-13; M1 (~1 mm ridge requirement); M3 (true scale); glossary relief/Ra/Rq + cutoff.

## Control baseline 2026-09-13 (ticket 02, measured + eye-confirmed)

PGSR-A control (`artifacts/review_A_stock/tsdf_fusion_post.ply`): 96,719 verts / 173,900 faces / 10 sherd-scale pieces, median triangle edge **0.77 mm** (the 0.75 mm grid, as M8 said). Rim relief character **p50 0.35 mm** RMS in an R = 1.5 mm ball (method-local Rq-like, same code reruns on QGS in 04). Steel **0.0 cm²** by component audit. Eye: coarse grid lumps with fusion holes, no 0.2 mm structure — this picture is the bar QGS must beat. Eye 2026-09-13: conservator confirms the reading — coarse blocks, edge detail not cleanly legible at this grid. PGSR-A side of the eye is closed; QGS side stages in 04. Pass/fail fraction deferred to 04 (one mesh alone has no reference to be "within" anything). Bundle rename 2026-09-14: image-only eye bundle moved out of the viewer registry (`visual-qa/preview/qgs_edge_baseline_r1.json`) so rescan lists only loadable 3D pairs; ticket 02/04 `Needs-eye:` refs updated, no figures changed.

## Pin 2026-09-13 (ticket 01, GO — no GPU spent)

- QGS `74d05c945e99fcaef7afe5a8831903be71ad9b55` (master HEAD via `git ls-remote`). PGSR stock HEAD `de24f1a38b350387e8d8fe381b2cd70c1ae946e7` unchanged (matches `provenance_A03.json` `stock_pin`); community pin `8777d4b` unchanged.
- Control: PGSR variant-A frame-correct stock-posed mesh (`PGSR/artifacts/review_A_stock/tsdf_fusion_post.ply`, from regs-off 30k `output/A03_noreg`; 96,719 verts, 10 forced pieces, 0.75 mm grid). Sep-12 fork-posed mesh excluded as INVALID displaced.
- Dataset: `A03_sherds` — 164 RGB JPEG 3200×2133, `images_rgba` baked (alpha mean ~2.3%), COLMAP sparse 164 registered. Full resolution, holdout every 8th view (`dataset.eval: True`, `hold: 8`).
- Extraction parity: voxel 0.002 units (0.75 mm via 373.73 mm/unit sidecar), sdf_trunc 5×voxel, depth_trunc 5.0 (QGS 3.0 default not used — far-side content reaches 4.81), num_cluster 10.
- Run values: 30k iters, one seed; `densify_grad_threshold 0.5`, `lambda_dist 50000`, `lambda_normal 0.05`, curvature losses 0, `depth_ratio 0.0` default; multi-view weights from iter 7000 (PGSR-regs-onset watch, not pre-disabled).
- Mask NATIVE GO: `dataset.use_alpha: True` + `images_rgba` (alpha-gated depth zeroing in `reconstruction()` and `extract_mesh_bounded()`). Layout accommodation: cluster dataset is flat `sparse/` (no `sparse/0`), QGS reads `sparse/0` — trial stages `sparse/0` compat symlinks, shared data untouched. Train entry: stock `train.py` `__main__` has the `training()` call commented out (eval-only as shipped), so a PGSR-side driver imports `training()` — no QGS fork change. Env: fresh conda env per QGS `environment.yml` (python 3.9.19, torch 2.2.2, open3d 0.18) + `diff-quadratic-rasterization` and `simple-knn` submodule builds, then import probe.
