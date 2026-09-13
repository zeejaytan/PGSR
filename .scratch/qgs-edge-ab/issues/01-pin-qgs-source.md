# 01: Pin QGS source and state the mask path

**What to build:** a pinned, repeatable starting line for the whole trial — QGS commit recorded in R1, control mesh named by path, dataset provenance present, voxel/band in mm stated, and the QGS mask construction stated (native, ported, or missing) with a GO/NO-GO before any GPU burns.

**Answers:** R1

**Blocked by:** None (can start immediately).

**Status:** resolved

- [x] R1 carries the QGS commit hash (from `will-zzy/QGS`), the PGSR variant-A control mesh path (frame-correct stock-posed mesh; Sep-12 fork-posed mesh explicitly excluded as INVALID displaced), and the `A03_sherds` dataset provenance (164 views, full-resolution flags, holdout discipline)
- [x] Voxel size and truncation band for the QGS extraction stated in millimetres with route sidecar; QGS run values recorded (`densify_grad_threshold`, `lambda_dist`, `depth_ratio`, curvature losses off unless justified, one seed, iteration count)
- [x] Mask construction for QGS stated: NATIVE via `use_alpha` + `images_rgba` (GO — see Answer; no port, no fork)
- [x] Env delta stated: fresh conda env per QGS `environment.yml` + both submodule builds (import probe); MILo-env additive route refused with reason (see Answer)
- [x] Link gate passes after this ticket (`check_intent_links.py` zero errors)

## Answer 2026-09-13

GO. All five boxes verified against pinned sources, no GPU spent.

- **QGS pin:** `74d05c945e99fcaef7afe5a8831903be71ad9b55` (`will-zzy/QGS` master HEAD via `git ls-remote`, 2026-09-13). PGSR stock HEAD `de24f1a38b350387e8d8fe381b2cd70c1ae946e7` unchanged — matches `provenance_A03.json` `stock_pin`, no drift; community pin `8777d4b` unchanged.
- **Control:** PGSR variant-A frame-correct stock-posed mesh — local `PGSR/artifacts/review_A_stock/tsdf_fusion_post.ply` (+ render), from regs-off 30k `output/A03_noreg` (M8 verdict: 96,719 verts, 10 forced pieces, 0.75 mm grid). Sep-12 fork-posed mesh excluded as INVALID displaced (withdrawn invert, M8 chain).
- **Dataset:** `A03_sherds` per `PGSR/provenance_A03.json`: 164 RGB JPEG 3200×2133, `images_rgba` baked (alpha mean ~2.3%), COLMAP sparse 164 registered. Full capture resolution, no downsample; holdout every 8th view (`dataset.eval: True`, `hold: 8` — QGS names, not PGSR's `-r/--eval` flags; exact keys confirmed at build).
- **Voxel/band (parity with M8):** `voxel_size 0.002` scene units × 373.73 mm/unit sidecar = **0.75 mm**; `sdf_trunc 5×voxel` (0.01 units ≈ 3.7 mm); `depth_trunc 5.0` (keeps far-side box content to 4.81 + margin per 09-11 max-depth check; QGS 3.0 default NOT used); `num_cluster 10`. Same units as PGSR (same COLMAP cameras).
- **QGS run values (base.yaml HEAD):** 30k iters; `densify_grad_threshold 0.5`, `lambda_dist 50000`, `lambda_normal 0.05`, curvature losses 0 (authors: unsatisfactory — stay off); `depth_ratio 0.0` default (1 only if render quality demands, stated if changed); multi-view NCC+geo weights engage at iter 7000 — same onset as the PGSR regs catch-22, watched not pre-disabled. One seed.
- **Mask — NATIVE GO:** `scene/cameras.py` `get_mask` reads the 4th RGBA band when `use_alpha` is set; `utils/mesh_utils.py` `reconstruction()` zeroes depth where mask < 0.5 and `extract_mesh_bounded(mask_backgrond=True)` zeroes depth where `gt_alpha_mask` < 0.5. Trial sets `dataset.use_alpha: True` + images folder `images_rgba`. No community fork needed. Layout accommodation (corrected 2026-09-13 — first note had it backwards): the cluster dataset is flat `sparse/` (verified, no `sparse/0`), QGS reads `sparse/0`, so the trial stages `sparse/0` compat symlinks; shared data untouched. Train entry: stock `train.py` `__main__` ships with the `training()` call commented out (eval-only), so a PGSR-side driver imports `training()` — no QGS fork change.
- **Env — fresh, not additive:** QGS `environment.yml` pins python 3.9.19 / torch 2.2.2 / open3d 0.18 plus `submodules/diff-quadratic-rasterization` + `simple-knn` (distinct from PGSR's `diff-plane-rasterization`). MILo-env additive route refused: interpreter + torch pins differ, so reuse-first probe fails by inspection — build per `environment.yml`, then submodule builds, then import probe.
- **Watch (not scope):** late-training NaNs (upstream issue #10) + multi-view onset at 7k. If the 7k→30k window smears like PGSR, that is a regs-off follow-up arm, not part of the base A/B.
- R1 pin section carries all of the above; boxes there stay unticked until the live run scores.
