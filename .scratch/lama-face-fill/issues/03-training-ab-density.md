# 03: Training A/B on inpainted vs control inputs, density figures

**What to build:** the two trainings that answer the density half of R2: arm A on LaMa-inpainted inputs (mask-free, production loss untouched), arm B the unmasked control — with density reported as counts, not impressions.

**Answers:** R2

**Blocked by:** 02 (held-out-patch check passed).

**Status:** in-progress
**Working in:** lama-train-runner (2026-10-13)

**Interview 2026-10-13:** Q1 fill all 33 A31 views full-res; Q2 A31-only subset both arms; Q3 confirmed dispatch.

- [ ] Both arms trained at full capture resolution, identical seed/config/iterations, every-8th-view holdout kept
- [ ] Gaussian counts A vs B, mesh vertex counts A vs B, kept-Gaussian footprint median/p90 in mm for both arms
- [ ] Laptop-side poll started on every submit; small renders/metrics in the landing zone, heavy data stays on the cluster
- [ ] No background-loss or pruning arm added (M5/M4 stay retired); the LaMa arm trains mask-free on filled inputs

## Evidence (2026-10-13, runner)

**A31-only subset construction (pre-built, both arms):**
- Paths: control `PGSR/data/17062025/A31_control/` (images/ + sparse/ + provenance.json); lama `PGSR/data/17062025/A31_lama/` (sparse/ done, images/ staged after fill verify). Outputs reserved: `PGSR/output/A31A_lama/`, `PGSR/output/A31B_ctrl/`.
- Sparse filter method (`lama_trial/ticket03/build_A31_dirs.py`): `read_model` on MILo `A03_sherds/sparse/0` (164 cams, PINHOLE 3200x2133 f=6829.81/6829.36 cx1600 cy1066.5, shared cam id 1); keep 33 entries named A31_1100-1132; rebuild each Point3D as a new namedtuple keeping only obs whose image id is kept (namedtuples immutable — first attempt failed `AttributeError: can't set attribute`, job 32809593 FAILED 1:0; fixed, job 32809646 COMPLETED 0:0 00:00:05); `write_model` flat sparse/ (cameras.bin + images.bin + points3D.bin).
- 33-cam reload verify: both arm sparse/ reload 33 cams named A31_1100-1132 in order; points 78227 -> 49396 (obs-filtered to 33 views). Control images/ 33 symlinks to MILo originals, first frame 3200x2133 verified.
- Train/test split (no split.json; default llffhold=8 on sorted 33): test idx [0,8,16,24,32] = A31_1100, A31_1108, A31_1116, A31_1124, A31_1132 (5 holdout, 28 train) — identical to full-164 holdout's A31 subset, holdout stays honest.

**Fill staging (done) + fill run (queued):**
- Masks: fill = complement of A03_erode0 tight sherd masks (mask white 2.0% = clay; fill white = background/clamp/rig/steel), 0px dilation, no feather, per-view 5568x3712->3200x2133 NEAREST, no cross-view propagation. Break never inpainted (inside sherd mask). 33 pairs in `lama_trial/ticket03/fill33/indir/` (<stem>.png RGB + <stem>_mask.png), manifest fill_frac mean 0.9800 min 0.9765 max 0.9846. Staged-copy-vs-true pixel-identical (A31_1116 check).
- Staging job 32808951 COMPLETED 0:0. Fill job 32809310 PENDING (Resources — queued behind GPU work, normal): gpu-a100-short 1 GPU 64G 4h, `bin/predict.py model.path=big-lama/big-lama indir=fill33/indir outdir=fill33/out` (predict writes `out/<stem>_mask.png` full-res). Polling via sacct; State/ExitCode on completion.
- Outside-mask Δ=0 check queued at verify (`verify_fill33.py`): per view assert shapes (2133,3200,3), max|Δ|=0 over mask==0, max|Δ|>0 over mask==255; any outside>0 = BLOCKED.

**Mask-scope HOLD (lead ruling 2026-10-13):** fill 32809310 HELD via `scontrol hold` (squeue showed `JobHeldUser`) — lead flagged fill_frac mean 0.98 = filling 98% background, not clamp-only; confounds arm A vs B and wastes GPU. Correct scope = clamp-occluded face ONLY. Trains NOT submitted. Subsets stand as-is. Clamp-only mask investigation next; no fill re-stage until lead rules.

**SSH note:** ssh_exec/ssh_list harness broken session-wide; laptop SSH via pwsh works (hold reconfirmed JobHeldUser 2026-10-13).

**Mask-scope investigation (runner 2026-10-13, eye-checked): PROPOSE jaw-contact-band fill; object-minus-sherd REJECTED.**

**Extraction ruling (lead):** both arms fuse at stock render.py 4x (sdf_trunc 0.008 units ≈ 2.99 mm band); pin states 5x (0.01 ≈ 3.74 mm) — delta one voxel ≈ 0.75 mm, identical both arms so comparison stays fair. render.py untouched per spec.

**Mask types on clamp-facing A31_1116 (all L 5568x3712 native, NEAREST to 3200x2133):** sherds white 0.0203 = clay only (11 comps in frame; A31 piece comp1 n=28796 bbox y144-467 x1456-1644 holds patch 1556,320); object 0.2496 = whole rig silhouette (clamps+rods+dial+all clay; contains 100% of sherd); measure 0.0419 = rig subset, 100% inside object, lum mean 92; dial 0.1145 = turntable+rod structures, lum mean 68.
**Candidate object-minus-sherd = 0.2294 of frame: REJECTED.** Only 0.52% of it touches A31 (dilate-30 ring test: touch frac-of-image 0.0012); lum mix dark-bg 10.7% / mid 42% / bright 47.3%; overlays (`A31piece_zoom_cand.png`, `A31_1109_face_cand.png`) show it paints rods, dial, background — NOT clamp-only.
**True geometry:** A31's clamp contact is EDGE-ON (jaws grip the sherd's lower edge; no face hole in this pose). Arc survey: piece bbox 233x295 (edge, 1100) -> 388x450 (face, 1109-1111) -> 111x311 (edge, 1123) -> 223x295 (1132); jaw contact is a narrow band at visible clay edge in every view.
**PROPOSAL (no staging until lead rules):** fill = dilate(sherd, r≈30px ≈ 6.6mm) ∩ (object-minus-sherd); predicted frac ≈ 0.001-0.01 (vs 0.98 now, 0.23 candidate). Keeps: break never inpainted (inside sherd), jaw-unseen excluded (outside ring+object), background untouched (outside object). Per-view gates: outside-mask Δ=0, in-mask Δ>0, frac<0.02.
**Lead ruling 2026-10-13 — APPROVE narrow-band direction, REJECT broad masks, re-stage gated:**
- REJECT complement-of-sherd (0.98, fills background) and object-minus-sherd (0.2294, paints rods/dial — only 0.52% touches A31). Overlays confirm both paint non-clamp rig.
- APPROVE proposal fill = dilate(sherd, r≈30px ≈ 6.6mm) ∩ (object−sherd), predicted frac 0.001–0.01, per-view gates (outside-mask Δ=0, in-mask Δ>0, frac<0.02). Keeps: break never inpainted, jaw-unseen excluded, background untouched.
- CONDITION before re-stage: one crop proving clamp visibly occludes A31 FACE (not edge-only) in at least one view; if no view shows face occlusion, STOP and report — the trial has no face to recover. Break/jaw-contact stays excluded.
**Face-occlusion CONDITION (runner 2026-10-13): PASSES — clamp visibly occludes A31 FACE in 1115-1119.**
- Identity correction: the first survey pass tracked the WRONG sherd (big triangular face, a neighbour). True A31 re-anchored from the ticket-02 patch (A31_1116 s3200 x1456-1644 y144-467 holds patch 1556,320 → native comp1 n=87282) and propagated both directions by bbox IoU+area score (`face_survey/track_true.json`). Chain 1100→1122 smooth (x-drift ~7px/view, area 53k→113k→20k); 1123-1132 track jumps to a neighbour sherd (x2687→3364 discontinuity) — identity there UNCERTAIN, flagged not used.
- Eye survey (33 contact-zone crops + `face_survey/contact_sheet_true.jpg`, laptop `artifacts/face_survey_contact_sheet_true.jpg`): 1100-1108 edge-on (no face); 1114-1120 A31 face turns to camera with black jaw tips overlapping the pale face interior; 1121+ swings edge-on again. Lead eye-check concurs (1114-1119 narrow band at lower face edge).
- Face-conditional measure (jawlike = lum<90 & |R-B|<15, calibrated jaw rubber meanRGB 57/59/61 R-B −3.7 vs break clay 102/90/82 R-B +20.3; occlusion = jawlike px inside A31 bbox whose 61px neighbourhood is >50% pale face lum>120): 1100 control 0 px; 1114: 23; 1115: 276 (1.9% of face); 1116: 419 (2.3%); 1117: 436 (2.1%, max); 1118: 404 (1.7%); 1119: 343; 1120: 87. Conservative lower bound (strict neighbourhood rule).
- Proving crops: laptop `artifacts/face_proof_A31_1116_face.jpg` + `_contact.jpg`, `face_proof_A31_1117_face.jpg`, `face_proof_A31_1118_face.jpg`; cluster `lama_trial/ticket03/face_survey/a31_111{6,7,8}_tface.jpg` + sheets. CITED VIEW: A31_1116 (lead-nominated anchor; 1117 measures max, 1118 clearest to the eye).
- Scale note: at the ticket's 30px≈6.6mm scale, ~420px occlusion ≈ 90mm² — a jaw-tip-sized strip, matching the narrow-band (not whole-face) expectation.

**Narrow-band re-stage (job 32855822 COMPLETED 0:0) + fill re-submit (job 32856094):**
- Old held fill 32809310 scancelled (sacct State CANCELLED); broad manifest preserved at `fill33/manifest_broad_backup.json`.
- New masks (`stage_fill33_narrow.py`, milo-env scipy, sbatch `stage_narrow.slurm`): fill = dilate(sherd,30) ∩ object ∩ ¬sherd at 3200x2133 NEAREST, RGB re-staged identical. Verbatim log: `staged 33 pairs; narrow_frac mean 0.01236 min 0.00907 max 0.01427` + `GATE frac<0.02: PASS`. Manifest `fill33/manifest_narrow.json` (per-view narrow/sherd/obj fracs). Mean 0.0124 slightly above the 0.001-0.01 prediction (band rings all ~10 sherds/frame, not A31 alone) — under the 0.02 gate.
- Overlay eye-check (`artifacts/narrow_check_1116.jpg`, zoom `artifacts/narrow_a31contact_1116.jpg`): thin red rings hug sherd outlines + red blobs at both A31 jaw tips covering the occlusion zone; rods/dial/background unpainted. Known imperfection: SAM object halo paints a ~30px background sliver along background-facing sherd edges (uniform black, inpaints black-with-black, no clay touched) — accepted, formula as approved.
- Fill resubmitted unchanged path (`fill33.slurm`, gpu-a100-short 1GPU 64G 4h, big-lama): job 32856094 RUNNING on spartan-gpgpu127, out/ filling (~3 min/view). verify_fill33.py (shapes/outside-Δ=0/inside-Δ>0) runs on completion; NO TRAINS until it passes.

**Fill VERIFIED (runner 2026-10-13) — trains may proceed at lead's call (not in this runner's orders).**
- sacct: `32856094 COMPLETED 0:0` (out/ 33/33, ~3 min/view on spartan-gpgpu127).
- Verbatim verify: `verified 33/33; all-ok=True`, `EXIT=0` (per-view shapes (2133,3200,3), max|Δ|=0 outside mask, max|Δ|>0 inside; full rows in `fill33/verify.json`).
- Spot stats A31_1116: outside_max 0.0, inside_max 216.0, inside_mean 15.9.
- Eye-check (`artifacts/fill_eye_1116.jpg`, orig vs filled contact zoom): jaw-tip band at sherd edge replaced with clay-toned fill continuous with the face, no smearing into face; jaws below the 30px band correctly remain.
- Superseded by the train-step authorization below (format decided: PNG bytes under .JPG names) — see submitted block.

**Train step SUBMITTED (runner 2026-10-13, lead-authorized) — both arms PENDING, no extraction.**

**Lead eye-check + format ruling 2026-10-13 (fill VERIFIED, trains AUTHORIZED):**
- Eyed `artifacts/fill_eye_1116.jpg` (orig vs filled): jaw-tip band replaced with clay-toned fill continuous with the face, no smear — faithful. Eyed `artifacts/narrow_check_1116.jpg`: thin rings hug all sherd outlines + blobs at jaw contacts, rods/dial/background unpainted — as approved. verify.json 33/33 outside_max 0.0 (lead re-read). Fill ACCEPTED.
- Format: BYTE-COPY PNG bytes to `A31_XXXX.JPG` names (no re-encode). Loader is extension-agnostic (`scene/cameras.py:33` PIL `Image.open`; path built from sparse basename `scene/dataset_readers.py:113`, so names must match sparse exactly). JPEG re-encode REJECTED (double-compresses lama arm only, breaks outside-Δ=0). Document bytes-vs-extension + sha/sizes in manifest; one PIL-decode check of a `.JPG`-named PNG.
- Authorized: build `A31_lama/images/`, verify 33 names + pixel/sha check, submit train_A31A (lama) + train_A31B (control) drafts after confirming `-r 1 --eval`, 30k iters, seed 22; laptop-side poll on every submit; report job IDs. No extraction until trains complete.

**Train step SUBMITTED (runner 2026-10-13) — both arms PENDING (Priority), no extraction.**
- Staged via canonical `build_A31_dirs.py --only lama` (job 32864473 COMPLETED, verbatim `A31_lama: 33 fills + provenance — OK`; asserts verify.json 33/33 all-ok): fill33/out/a31_XXXX_mask.png → `A31_lama/images/A31_XXXX.JPG` (PIL PNG-save, NO JPEG re-encode).
- Provenance `A31_lama/provenance.json` fill line patched to narrow-band + jobs (build-script text described the retired broad mask); fill_history records held/cancelled 32809310.
- Manifest `A31_lama/images/manifest_copy.json` (33 sizes/sha); PIL check verbatim: `format=PNG size=(3200, 2133)` on a .JPG-named file; all 33 pixel-identical vs fill33/out/ at (2133,3200,3).
- Names: sparse(33, via read_model) == disk(33) == A31_1100-1132 expected — True.
- Drafts confirmed: `train.py -s <arm> -m <out> -i images -r 1 --eval` both arms; 30k = `arguments/__init__.py:79 (iterations = 30_000)`; seed 22 = `train.py:46 setup_seed(22)`; --eval → `dataset_readers.py:148 readColmapSceneInfo(...,llffhold=8)`; test/save default [7000,30000]. (A31B header comment mislabels "arm A" — cosmetic, DATA_DIR/OUT_DIR correct.)
- Submitted: arm A (lama) 32864742, arm B (control) 32864743 (gpu-a100, 1GPU, 12h). Verbatim squeue/sacct at handoff: both `PENDING (Priority)` — queued behind GPU work, normal. Foreground laptop-side poll ran 15 rounds; queue wait is the binding constraint, not a stuck job. Outputs: `PGSR/output/A31A_lama/`, `PGSR/output/A31B_ctrl/`.

**Trains COMPLETED (lead poll 2026-10-14) — sacct State/ExitCode recorded, no extraction yet.**
- sacct: `32864742|pgsr-A31A-lama|COMPLETED|0:0|2026-10-13T18:02:30|2026-10-13T20:43:42` (~2h41); `32864743|pgsr-A31B-ctrl|COMPLETED|0:0|2026-10-13T18:02:30|2026-10-13T20:50:02` (~2h47). squeue empty (left queue). Laptop-side poll via pwsh ssh (squeue+sacct), not scripts/slurm_poll.ps1 — deviation noted.
- Manifest flag resolved: `A31_lama/images/` lists 34 entries = 33 `A31_1100-1132.JPG` + `manifest_copy.json`; control `images/` 33. Loader builds paths from sparse basenames (`scene/dataset_readers.py:113` + `scene/cameras.py:33` PIL open), so the sidecar JSON is ignored — HARMLESS, no training pollution. Both arms ran 30k iters to completion.
- Density (counts, from logs + PLY sizes): arm A 673,742 points (`point_cloud.ply` 160M); arm B 631,016 points (150M). LaMa arm holds ~6.8% more Gaussians. Footprint median/p90 in mm + mesh vertex counts NOT yet scored — extraction seam next.
- Fit (log ITER lines): arm A train L1 0.0180 PSNR 26.59 / test L1 0.1557 PSNR 12.44; arm B train L1 0.0157 PSNR 27.64 / test L1 0.1521 PSNR 12.37 (iter 30000). Both arms show the same test-PSNR drop from iter 7000 (~20.5) to 30000 (~12.4) — shared overfit-to-train-views pattern, not an arm difference. No verdict among method-failed / measurement-broken / reference-wrong at this seam.
- Extraction submitted as Slurm job `32902442` from `slurm/pgsr_extract_lama_ab.slurm 0.002 10`; both arms use stock `render.py`, full-resolution `images`, 0.002-unit voxels, 4× SDF truncation (0.008 units ≈ 2.99 mm), 10 clusters, and no test render. Laptop poll ran `C:\PR\scripts\slurm_poll.ps1 32902442 60` to completion. Submission requested `gpu-a100-short`, but Spartan's submit hook overrode to `gpu-a100` because the script requests 256G (short partition cap 123750M).
- Extraction COMPLETED (lead verify 2026-10-14): sacct `32902442|pgsr-extract-lama-ab|COMPLETED|0:0|2026-10-14T05:18:43|2026-10-14T05:24:26` (~6 min run after Priority queue wait). Both arms rendered 28 train views (33 minus 5 llffhold test) and fused at the approved grid. `mesh_stats.py` (open3d, in-job) verbatim: A post `verts 5128774 tris 9669832 clusters 10 top5 [734134, 788959, 1226222, 1371628, 4349171] span [1.558, 3.872, 3.4441]` (raw 10697082 verts, 477M); B post `verts 5876742 tris 10997543 clusters 10 top5 [113055, 117599, 1903576, 2355815, 5995694] span [1.624, 3.9103, 2.649]` (raw 11025029 verts, 493M). Post files on cluster: A `tsdf_fusion_post.ply` 264M, B 302M. Figures recorded, NOT interpreted — vertex counts alone say nothing about face detail or wall noise.
- First-look render COMPLETED (lead inspect 2026-10-14): CPU job `32906039` (sapphire; site retired cascade's old nodes, script amended + resubmitted) ran `scripts/measure_edge_baseline.py` on both post meshes, sacct `COMPLETED|0:0|05:30:04|05:32:19`. Small outputs fetched to `artifacts/edge_AB/` (stats.json + relief_hist/context/closeup_0/1 PNGs per arm; meshes stay on Spartan). Vertex counts cross-check exactly with extraction figures.
- Render verdict (eye on all fetched PNGs, mm labels provisional on the A03 373.733 scale): fusion SANE at gross level — both arms show the same tray-scale scene (~1.4 m span), 10 clusters, no collapse, no rig steel. BUT the auto-crop close-ups MISSED the sherd: they frame torn fusion-boundary sheets at different scene spots per arm (crop centres ~470 mm apart), i.e. mesh-boundary tears, not sherd faces, and not mutually comparable. Cause (measurement, not method): the script's "largest-component rim" rule was built for the isolated A03 sherd mesh; on full-scene 5M-vert meshes the largest component is tray background. Relief figures are scene-dominated (tray): A p50 0.065 / p90 0.241 vs B p50 0.065 / p90 0.25, tri-edge p50 0.764 both — background agreement only, says nothing about face detail. No A-vs-B face verdict from these renders.
- Handoff to 04/05: scoring + eye crops MUST target the sherd's known 3D location (photo masks / COLMAP frustums), not auto-max-residual; 04 must attach scale provenance before any scored number counts. Ticket 03's render seam is done; no geometry claim beyond gross sanity stands.
