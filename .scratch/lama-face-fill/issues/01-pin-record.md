# 01: Pin LaMa build, mask construction, and measurement record

**What to build:** the repeatable source record the whole trial stands on: LaMa commit + weights named, inpaint mask construction stated, extraction voxel/band in mm stated, control inputs named — so that every later ticket runs something pinned, not something that drifts.

**Answers:** R2

**Blocked by:** None (can start immediately).

**Status:** done
**Working in:** DSH lead session (2026-10-12)

## Pin record (2026-10-12, verified this session)

- LaMa repo `https://github.com/advimman/lama`, HEAD `786f5936b27fb3dacd2b1ad799e4de968ea697e7` (via `git ls-remote`, laptop + Spartan agree); weights: `big-lama` — `https://huggingface.co/smartywu/big-lama/resolve/main/big-lama.zip` (README "best model (Places2, Places Challenge)"); fallback all-models Google Drive `1B2x7eQDgecTL0oh3LSIBDGj0fTxs6Ips` not used unless big-lama fails to fetch.
- Control inputs: `/data/gpfs/projects/punim2657/MILo/data/17062025/A03_sherds/` — `images/` 164 RGB JPG 3200x2133 (arcs A31×33, A32×33, A33×32, A34×33, A35×33), `sparse/` COLMAP (164 registered), `capture.json` (`llffhold` 8, `train_images_arg` images_masked, sherd masks `masks_sherd_png/` 21 files note: full 164-mask set at `/data/gpfs/projects/punim2657/MILo/masks/17062025/A03_erode0/masks_sherds/`). PGSR side `data/17062025/A03/images` symlinks to the MILo images dir; provenance: tight erode0 outlines, NEAREST-resized 5568x3712→3200x2133, mean sherd coverage 2.28% (min 1.49%, max 3.06%).
- One sherd: **A31** (33 views `A31_1100–1132`, same 3200x2133) — first arc, keeps the A/B to one turntable run; other arcs out of scope until the base A/B passes.
- Training pins (both arms identical): 30,000 iterations (`PGSR/arguments/__init__.py:79`), seed `setup_seed(22)` (`PGSR/train.py:40-46`), production loss untouched; every-8th-view holdout kept (`llffhold` 8).
- Extraction pins (both arms identical, M8 parity): `voxel_size 0.002` scene-units = **0.75 mm** (373.73 mm/unit sidecar), `sdf_trunc 5×voxel = 0.01`, `depth_trunc 5.0`, `num_cluster 10` (per `PGSR/slurm/qgs_a03.yaml:11-13`, `PGSR/scripts/qgs_run_extract_masked.py:55-56`).
- Env reuse-first: `/data/gpfs/projects/punim2657/MILo/envs/milo` (py 3.9.23, torch 2.3.1+cu118, torchvision 0.18.1, cv2 4.11.0, omegaconf ok); import probe **failed only on `albumentations`** (LaMa dep) → additive delta is `pip install albumentations` into the same env; no fresh env.

- [x] LaMa commit hash + weights recorded in R2 before anything runs
- [x] Mask construction stated: which pixels (clamp/rig only), dilation px, cross-view propagation; break pixels and jaw-contact region explicitly excluded
- [x] Extraction voxel size and truncation band stated in mm for both arms; control input dataset named with view count and resolution
- [x] One sherd chosen and named; identical seed/config/iterations recorded for both arms
- [x] Env reuse-first: existing Spartan env named with the additive delta (if any) stated; fresh env only on a failed import probe

Mask construction (binding): inpaint mask = complement of the `A03_erode0` tight sherd masks (clamp/rig/steel only), **0 px dilation, no feather** (same TIGHT rule as `PGSR/scripts/bake_rgba.py:9-10`), per-view at 3200x2133 NEAREST, no cross-view propagation (each view inpainted independently at full res). Break pixels are never inpainted (break is inside the sherd mask; clamp sits on face only). Jaw-contact region (unseen in all views) is excluded from fill and from scoring.
