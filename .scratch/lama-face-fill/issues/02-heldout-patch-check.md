# 02: Inpaint held-out face patch and check it tracks known skin

**What to build:** the stop-or-go gate for the whole trial: a known face patch held out, filled by the pinned LaMa build, and compared to its true surface — so that clamp holes are only touched by a fill already shown to track real skin.

**Answers:** R2

**Blocked by:** 01 (pin record).

**Status:** resolved (photo seam closed 2026-10-13; binding surface check moves to 03/04)

## Conservator eye note (2026-10-13 — proceed to clamp)

- Lead asked what is judged: whether the hidden 10.6 mm square reads as the same plain wall or invents something (three checks: box disappears / no invented texture / no break leak-in).
- Conservator verdict: **proceed to clamp** (m00617).

- [x] Held-out known face patch filled at full photo resolution; deviation from true surface reported in mm
- [x] Patch deviation within the face tolerance stated in R2; if it misses, the trial stops here and R2 records the miss with a date — photo-proxy 1.215 mm does NOT bind (photo-domain, no surface); no MISS recorded, binding 0.5 mm check moves to 03/04; eye note proceed to clamp 2026-10-13
- [x] Patch close-up renders staged at a view resolving fine face texture, before any clamp pixel is touched
- [x] Jaw-contact region confirmed excluded from fill and from damage-scoring

**Lead note (2026-10-12, for review):** pick the representative view by inspecting images for large quiet flat wall + small clamp occlusion directly — A31 mask-coverage % ranks framing only (masks are sherd outlines, clamp sits inside them). Full 164-mask set: `/data/gpfs/projects/punim2657/MILo/masks/17062025/A03_erode0/masks_sherds/`; the 21-file `masks_sherd_png` subset is the held-out set only.

## Evidence (2026-10-12)

**Verdict: BLOCKED at import gate — no patch filled, no pixels touched, no deviation scored.**

Gate step: verify pinned-commit inference driver imports with only the albumentations delta.

Exact import probe (milo env python, `sys.path` → pinned `lama/` checkout `786f5936b27fb3dacd2b1ad799e4de968ea697e7` confirmed via `git rev-parse HEAD` on Spartan):

`from saicinpainting.training.data.datasets import make_default_val_dataset`

Verbatim failure (EXIT 1):

`File "/data/gpfs/projects/punim2657/PGSR/lama_trial/lama/saicinpainting/training/data/datasets.py", line 6, in <module> import albumentations as A — ModuleNotFoundError: No module named 'albumentations'`

Remediation attempt (per ticket pin, albumentations-only): `pip install "albumentations==0.5.2"` inside shared `/data/gpfs/projects/punim2657/MILo/envs/milo` via CPU holder job 32764213 (`srun --overlap`). Result: pip resolved numpy 1.26.4 → 2.0.2 + `opencv-python-headless 5.0.0.93` + `imgaug 0.4.0` + `Shapely 2.0.7`; then `import albumentations` failed with `AttributeError: np.sctypes was removed in the NumPy 2.0 release` (via `imgaug/imgaug.py:45 NP_FLOAT_TYPES = set(np.sctypes["float"])`). So the pinned `albumentations==0.5.2` + `imgaug==0.4.0` pair is incompatible with the numpy it pulls in — no workaround applied per ticket (stop, no workarounds; only the ticket-authorized delta is permitted).

Shared-env restore (same CPU holder, single-task `-n1` to avoid parallel-pip races): uninstalled albumentations/imgaug/Shapely, reinstalled `numpy==1.26.4`. Verified: `numpy 1.26.4` imports; `cv2 5.0.0` imports. Residue noted: `opencv-python-headless 5.0.0.93` remains installed and pip flags it as requiring `numpy>=2` (incompatible with restored 1.26.4), but `cv2` imports fine — lead to decide whether to remove it. No other env deltas left by this ticket.

What did NOT happen (gate stopped before all of it): no A31 view picked, no held-out patch defined, no `predict.py` invocation (LaMa command never ran), no `measure_patch_deviation.py` built, no close-ups rendered, no clamp pixels touched, no jaw-contact check, no training, no intent edits, no commits.

Jobs: no `sbatch` submitted → no `sacct` State/ExitCode to record. Holders observed only: CPU `cpu-session` 32764213 RUNNING (used, left running for lead), GPU `gpu-session` 32764212 PENDING (not used, left alone), `claude-rc` 32754924 RUNNING (unrelated, untouched). Spartan PGSR repo `git status --short` shows pre-existing `M render.py` + staged new scripts — none touched by this ticket.

Unverified: whether a clean-room venv (not the shared milo env) could satisfy the pinned LaMa requirements; which numpy/pin combo the lead wants; the view/patch choice; the full 3200×2133 fill path.

**Needs-eye:** lead decision needed — (a) authorize a LaMa-capable env outside shared milo (or a different remediation), or record ticket 02 as env-blocked; (b) confirm shared-env residue (`opencv-python-headless 5.0.0.93` vs numpy 1.26.4) is acceptable or direct its removal.

## Evidence (2026-10-12) — single-view gate run, face-only patch

**Verdict: MISS on literal photo-proxy (>0.5 mm); true surface-deviation mm UNVERIFIED — no clamp pixels touched, trial stops here pending lead ruling on metric.**

- View/patch reason: A31_1116 (sparse id 29, PINHOLE 3200x2133 f≈6829.8/6829.4 cx1600 cy1066.5) picked per lead note for large quiet flat wall + small clamp. Patch is face-only wall skin: cx=1556 cy=320 size=48 (x0=1532 y0=296), 48px ≈ 10.57 mm side at 0.2203 mm/px. Staged asserts: frac-clay 1.0000, box gray mean 154 std 6, darkfrac(<90) 0.0000. First 88px box (cx1549 cy300) STRADDLED the face/break boundary (lead eye) and was discarded; shifted-box +48px run failed (frac-clay 0.64, outside sherd); 48px scan found this pure-face box. Re-projects inside clay in neighbours was proven only for the old 88px box (A31_1115 uv 1532,296 + A31_1117 uv 1568,332 in_clay true); NOT recomputed for the new 48px box — unverified.
- Orientation/frame lock (lead Q): stored/training frame is landscape 3200x2133 (W x H): PIL `Image.open` size (3200,2133) exif274=8, `images_masked` RGBA (3200,2133), COLMAP cameras.bin `PINHOLE 3200 2133`, erode0 mask (5568,3712)→NEAREST 3200x2133, LaMa `load_image` (PIL, no exif_transpose) + PGSR `readColmapCameras`/`LoadImage` (PIL, no transpose) both read stored frame. EXIF-8 display frame is portrait 2133x3200 (90° rotated; cv2 default-apply gave HWC (3200,2133,3), IGNORE_ORIENTATION gave (2133,3200,3)). Ticket-01 `3200x2133` pin HOLDS for training inputs. Staged `A31_1116.JPG` + `A31_1116_mask.png` share stored frame pixel-for-pixel: mask 48x48=2304 px at x0=1532 y0=296, output-vs-true max|Δ| outside dilated box = 0, in-box max|Δ| = 24.
- LaMa command (pinned commit 786f5936b27fb3dacd2b1ad799e4de968ea697e7 via `git rev-parse HEAD`; weights `big-lama/big-lama/{config.yaml,models/best.ckpt}`; isolated env `/data/gpfs/projects/punim2657/PGSR/envs/lama02`, shared milo untouched — `import albumentations` still ModuleNotFoundError there):
  `TORCH_HOME=gate02/torchhub PYTHONPATH=lama_trial/lama; cd lama_trial/lama; /data/gpfs/projects/punim2657/PGSR/envs/lama02/bin/python bin/predict.py model.path=/data/gpfs/projects/punim2657/PGSR/lama_trial/big-lama/big-lama indir=/data/gpfs/projects/punim2657/PGSR/lama_trial/gate02/indir outdir=/data/gpfs/projects/punim2657/PGSR/lama_trial/gate02/out`
  (dataset `InpaintingDataset` kind=default img_suffix=.png pad_out_to_modulo=8; needs lowercase `.png` copy alongside `_mask.png`; predict writes `outdir/<mask-rel-indir>` so output is `out/a31_1116_mask.png`. `indir/a31_1116.png` is a pixel-identical staging copy — mean|Δ| vs true 0.0000 — NOT the fill. predict.py runs on CPU device per code despite 1-GPU sbatch.)
- Jobs/sacct: 32801872 CANCELLED 0:0 (staged old straddling 88px box, killed before run); 32802000 FAILED 1:0 00:00:10 (`FileNotFoundError: .../indir/a31_1116.png` — jpg/mask suffix mismatch); 32802357 COMPLETED 0:0 00:02:34 (fill). Laptop-side polls were `squeue`+`sacct` watches, not `scripts/slurm_poll.sh` — deviation noted. Holders: cpu-session 32798559 RUNNING (used), claude-rc 32754924 RUNNING (untouched).
- (1) Deviation: filled `gate02/out/a31_1116_mask.png` verified full-res (2133,3200,3); method = gray-level |Δ| inside 48x48 box (N=2304 px) via `PGSR/scripts/measure_patch_deviation.py` (116 lines; box stats lines 44-70, renders lines 72-100): gray mean_abs 5.51 rms 6.98 p50 4.67 p90 11.67 max 22.0 bias −1.48 (levels 0-255). Photo-proxy mm = gray × 0.2203 mm/px (pinhole at patch sparse-median depth 4.0252u, N=620): mean_abs 1.215 rms 1.538 p90 2.570 max 4.847 mm. Scale: FX=6829.8123366747, MM_PER_UNIT=373.733 (`measure_edge_baseline.py:29`), depth patch-sparse-median.
- (2) PASS/MISS: MISS under literal mm_proxy (1.215 > 0.5) — BUT mm_proxy is a photo-domain proxy, NOT a surface deviation (see script `note` field + stats.json). True mm surface deviation is UNMEASURED (no mesh/fusion in this single-view gate). Conservator reading: this is **measurement-broken, not method-failed** — the fill is visually faithful (see close-ups) but the ticket's mm-surface instrument does not exist at this seam. No clamp pixels touched; no training started.
- (3) Close-ups (all under `C:\PR\PGSR\artifacts\lama02_eye\`, 1:1 pixels ≈ 0.22 mm/px so single pixels resolve the 0.2 mm ridge scale):
  - `gate02_side_by_side.png` — padded context, green 48px box on true (left) vs fill (right); fill tracks tone/grain, no edge or structure invented.
  - `gate02_true_1to1.png` — held-out answer skin 1:1 (48px = 10.57 mm); pale smooth face grain.
  - `gate02_fill_1to1.png` — LaMa fill 1:1; same grain class, slightly softer, no break texture dragged in.
  - Also staged: `gate02_patch_context_900_v2.png` (face-only proof: box fully on pale skin, break band well left), `gate02_overlay.jpg`, `gate02_patch_true_crop.png`, `gate02_stats.json`.
- (4) Jaw-contact exclusion: fill mask = ONLY the 48px face box (rest of mask black; outside-dilated-box max|Δ|=0 proves nothing else changed). Break never inpainted (box darkfrac 0, far from break rim in context crop). Jaw-contact (unseen-in-all-views) region never masked, never filled, never scored (score N = box pixels only). Clamp jaws grip the sherd's lower third; patch sits far above on open wall — confirmed on `patch_context_900.png` (clamp + jaws visible, box well clear).
- Unverified: true surface-deviation mm (needs fused-mesh instrument — tickets 03/04 territory, not built); neighbour reprojection for the new 48px box; which wall (inner vs outer — single view cannot tell, but clamp holes sit on wall faces either way); GPU-vs-CPU inference equivalence (ran CPU path); `scripts/slurm_poll.sh` was not used for these sbatches.

**Needs-eye:** conservator look requested — `gate02_side_by_side.png` + 1:1 true/fill pair under `C:\PR\PGSR\artifacts\lama02_eye\` (face-only 48px patch; lead eyed, faithful + slightly softer). Trial paused before clamp until the eye note lands.

## Lead ruling (2026-10-12/13 — verified, eyes on)

**Lead verdict: photo-gate PASSES its fail-fast purpose; the photo-proxy "1.215 mm" does NOT bind against the 0.5 mm face tolerance. Trial PAUSED before clamp pending conservator eye note — not stopped as MISS.**

- Recomputed on Spartan (lead, milo python): inbox mean|F-T| 5.5133, max 22.0; outside-dilated-box max 0.0000; staging-copy-vs-true 0.0000. Shapes all (2133,3200). Confirms (a) `out/a31_1116_mask.png` is the scored fill, (b) nothing outside the box changed, (c) numbers in Evidence §(1) stand.
- Eyes on (lead): `gate02_side_by_side.png` — fill tracks tone/grain, no edge or structure invented; `gate02_true_1to1.png` vs `gate02_fill_1to1.png` — same grain class, fill slightly softer, no break texture dragged in. Face-only re-pick approved from `gate02_patch_context_900_v2.png`.
- Why the proxy can't bind: gray×mm/px converts a photo residual into length units but measures no surface — R2's 0.5 mm tolerance is a surface-deviation tolerance, and no mesh/fusion exists at this seam. Recording MISS on it would be measurement-broken reported as method-failed (standing rule: name which of the three). So: no PASS recorded either — binding mm check moves to the mesh scoring seam (tickets 03/04 instrument), where the same 0.5 mm tolerance applies to fused-surface deviation.
- Scorer `PGSR/scripts/measure_patch_deviation.py` (116 lines) APPROVED as the photo-seam instrument: refuses loudly on bad inputs, states its own proxy limit in its `note` field. Jaw-contact exclusion confirmed (score N = box pixels only).
- Wrap-up (runner 2026-10-13): cpu-session holder 32798559 released; shared milo pristine (numpy 1.26.4 + cv2 4.11.0, albumentations absent); jobs 32801872 CANCELLED / 32802000 FAILED 1:0 00:00:10 / 32802357 COMPLETED 0:0 00:02:34; `claude-rc` 32754924 untouched.

**Status:** resolved (photo seam closed 2026-10-13; mesh seam closed 2026-10-14 via 04 honest-negative; witnessed note in 05)
