# 11: Save the face blobs — diagnose steel-vs-sunk, then intervene

**What to build:** the retry, in two gated phases. Ticket 10 named the killer (observe<2 trim, 99.86% at iter 8000) and the lead's follow-up showed the flag counts front-visible contributors only. What it did NOT settle: are the true face-surface blobs steel-blocked in the views that matter, or sunk inside the clay? The fix differs, so phase A diagnoses, the lead picks, phase B intervenes.

**Answers:** R2

**Blocked by:** none (conservator chose diagnose-then-fix 2026-10-15).

**Status:** resolved

## Answer (lead ruling 2026-10-16, reseed curve eyed — RESEED FAILED)

Replanting 6,593 measured face seeds at iter 8001 did not stick: cover held to iter 9000, then the iter-9000/10000 trims removed all of them (0 in box at 30k) — same rule, not a new failure. The foregone confirmatory fusion was cancelled (a mesh of an empty box teaches nothing). Standing result: face points never count as seen by the face-view cameras (dim, small — hidden behind existing geometry), so no planting strategy survives this trimmer. Remaining options, untried: (1) face-box trim exemption (protects whatever is there, junk or not), (2) find why face cameras don't count face points (rasterizer visibility), (3) different surfacing. None funded yet.

**Gate pick (lead, 2026-10-15, overlay + chart eyed):** NOT steel-blocked — 1101–1105 zero steel-on-face, priority views ≥98% clear, yet the global wipe still took 99.86%. The blobs sank inside. Exemption parked; reseed picked: re-plant at the 6,593 measured SfM face-seed positions right after the iter-8000 wipe, continue to 30k, re-fuse stock grid, render the box. One arm (B_ctrl) proves mechanism; A/B comparison waits for a surface in at least one arm.

- [x] Phase A — steel-vs-sunk (CPU only): NOT steel — five views zero occlusion, priority ≥98% clear. Blobs sank inside.
- [x] GATE: reseed picked (sunk-inside); exemption parked; relaxation not forced.
- [x] Phase B — reseed retrain on B_ctrl (33039064 COMPLETED 0:0): seeds held to 9000, trims took all by 10000; confirmatory fusion cancelled as foregone. No surface.
- [x] Restraint: no LaMa-vs-control claim; smalls in `artifacts/edge_11/`; work-notes only, never commits.

**Rules carried over:** renders before numbers; mm provisional; heavy compute on Spartan only.

## Worker work-notes (t11-saver, 2026-10-15 — PHASE A ONLY, staged, STOPPED)

Job receipts (sacct JobID|JobName|State|ExitCode|Start|End; all sapphire CPU-only):
- 33037212|pgsr-blk11|COMPLETED|0:0|2026-10-15T12:49:25|2026-10-15T12:49:53 (first pass; box-ROI denominator diluted fractions — SUPERSEDED, kept on cluster only)
- 33037434|pgsr-blk11|COMPLETED|0:0|2026-10-15T12:52:42|2026-10-15T12:53:07 (final; face-denominator fractions + steel-on-face-only overlays)
Laptop-side poll on submit; sacct State/ExitCode recorded. No GPU spent. Never committed/pushed.

Method (script `scripts/diag_block_11.py`, slurm `slurm/pgsr_diag11_block.slurm` — both NEW, uncommitted; cluster copies under `work/edge_11/`):
- Projected the ticket-10 face box (centroid [-0.1812, 0.4883, -0.1933], half-edge 0.115) through the SHARED 33-camera sparse model. Geometry is shared between arms, so one arm's cameras suffice — stated: A31_control sparse. Photos are A31_control originals (steel-visible; the LaMa arm's fill paints clay tone over the jaw band, so it cannot witness steel).
- Face ROI per view = bbox of the 8 projected box corners, clipped to frame. Constrain rule = ticket-06's (centroid inside A31 mask bbox + train view + renders_depth present) — reproduces ticket-06's 19-view list EXACTLY (1101-1107, 1109-1115, 1117-1121).
- Three numbers per view inside the ROI: (a) jawlike-raw frac (lum<90 & |R-B|<15, ticket-03 jaw calibration — overcounts on dark background, upper bound only); (b) PRIMARY conservative steel-on-face count: jawlike px whose 61px neighbourhood is >50% pale face (lum>120), i.e. steel sitting ON visible clay = genuinely in front; reported as fraction of pale-face px in the ROI; (c) narrow-band mask proxy (fill33 narrow mask white px / ROI px).
- Validation: conservative counts reproduce the ticket-03 cited occlusion px almost exactly (1114: 20 vs 23; 1115: 273 vs 276; 1117: 432 vs 436; 1118: 392 vs 404; 1119: 314 vs 343; 1120: 86 vs 87) — same jaw tips, independent code path. Rendered JET depths shown as pictured context only (per-view normalised, no metric read).
- Eyed: `overlay_A31_1117.png` (max-occlusion view; red = only the jaw-tip strip on pale clay, cyan box = projected face box, JET depth shows the ticket-06 near-blob at centroid) + `blocked_coverage.png` (19-view chart). First-pass overlays painted raw-jawlike red (whole dark background red — overstated); final overlays paint conservative-only red. Numbers below are the final pass.

Per-view front-blocked table (primary = face-blocked = cons steel / pale-face px; 19 constraining train views):

| view | train | pale px | cons steel px | face-blocked | mask frac | cited |
|---|---|---|---|---|---|---|
| 1101 | y | 3212 | 0 | 0.0000 | 0.0325 | — |
| 1102 | y | 2021 | 0 | 0.0000 | 0.0284 | — |
| 1103 | y | 1998 | 0 | 0.0000 | 0.0352 | — |
| 1104 | y | 1940 | 0 | 0.0000 | 0.0443 | — |
| 1105 | y | 2199 | 0 | 0.0000 | 0.0490 | — |
| 1106 | y | 9290 | 56 | 0.0060 | 0.0468 | — |
| 1107 | y | 36418 | 3185 | 0.0875 | 0.0484 | — |
| 1109 | y | 46891 | 2327 | 0.0496 | 0.0494 | — |
| 1110 | y | 40348 | 2200 | 0.0545 | 0.0522 | — |
| 1111 | y | 21096 | 1079 | 0.0511 | 0.0636 | — |
| 1112 | y | 13380 | 141 | 0.0105 | 0.0528 | — |
| 1113 | y | 8478 | 19 | 0.0022 | 0.0403 | — |
| 1114 | y | 11152 | 20 | 0.0018 | 0.0352 | 23 |
| 1115 | y | 15563 | 273 | 0.0175 | 0.0301 | 276 |
| 1117 | y | 21695 | 432 | 0.0199 | 0.0326 | 436 |
| 1118 | y | 23744 | 392 | 0.0165 | 0.0392 | 404 |
| 1119 | y | 27874 | 314 | 0.0113 | 0.0799 | 343 |
| 1120 | y | 19133 | 86 | 0.0045 | 0.1164 | 87 |
| 1121 | y | 27706 | 293 | 0.0106 | 0.1363 | — |

Full per-view JSON (all 33 views, both fractions + counts + ROI + depths): `artifacts/edge_11/block_table.json`.

Flat observations (no verdict — numbers for the lead's gate pick):
- Steel blocks 0 of 19 views in any load-bearing sense: the max is 8.75% (1107, edge-on), and the 6 priority face views are 0.18%–1.99% blocked (≥98% of visible face clear in every one).
- Sightlines perfectly clear in 5 views (1101–1105: zero steel-on-face px), yet the iter-8000 trim killed 99.86% of face points globally — the wipe cannot be explained by steel occlusion in the views that matter.
- The anchor view A31_1116 (max cited occlusion, 419 px) is an llffhold test view — never trained, never fused; it constrains nothing.
- Mask proxy (0.03–0.14) corroborates the narrow-band scale; higher at 1119–1121 where the dilate-ring catches background-facing edges (known SAM-halo sliver, ticket-03 accepted).

Files staged (NEW `artifacts/edge_11/`, small files only): `block_table.json` (33-view table), `blocked_coverage.png` (19-view chart, eyed), `overlay_A31_{1114,1115,1117,1118,1119,1120}.png` (face projection + steel-on-face in red + JET depth context; 1117 eyed). Cluster originals: `work/edge_11/report/`. Staged laptop scripts (uncommitted): `scripts/diag_block_11.py`, `slurm/pgsr_diag11_block.slurm`.

Deviations/limits: (1) pinned-repo `pull --ff-only` NOT run — the checkout carries pre-existing local modifications (render.py note + staged scripts, same as ticket-10 logged); a pull risked disturbing them, my work adds no repo files, so I verified read-only and report instead. (2) First-pass run superseded (diluted denominator); final pass re-ran end-to-end, numbers above are final. (3) No LaMa-vs-control claim anywhere; mm provisional.

Gate options restated (lead picks; no proposal here): (1) face-box exemption from the trim if steel-blocked; (2) post-wipe reseed + continued training if sunk-inside; (3) rule relaxation only if the evidence forces it.

STOPPED after staging — zero fix work, no retrain started.

## Worker work-notes (t11-saver, 2026-10-15/16 — PHASE B reseed, staged, STOPPED for ruling)

Job receipts (sacct JobID|JobName|State|ExitCode|Start|End):
- 33038536|stage_seeds_11|COMPLETED|0:0 (sapphire CPU; staged 6,593 face seeds from the sparse cloud — exact ticket-07 match; ticket-03's 49396 was a typo for 49936)
- 33039064|pgsr-reseed11|COMPLETED|0:0|2026-10-15T16:49|2026-10-15T19:26 (~2h36 on gpu-a100; B_ctrl recipe + iter-8001 injection, out `work/edge_11/B_ctrl_reseed`)
- 33106306|pgsr-cover11|COMPLETED|0:0 (sapphire CPU; cover check, seconds)
- 33106307|pgsr-fuse-reseed11|PENDING at write time (gpu-a100; stock-grid re-fusion queued — mesh verdict follows)
Laptop-side poll on every submit. Never committed/pushed.

Method (copy-trainer discipline — pinned repo files untouched; NEW uncommitted files: `scripts/reseed11/` = trace10-pattern copy with `reseed_face()` + iter-8001 hook + `RESEED11_SEEDS` preload, `slurm/pgsr_train_reseed11.slurm`, `scripts/stage_face_seeds_11.py`, `scripts/diag_cover_11.py`, `slurm/pgsr_cover11.slurm`, `slurm/pgsr_fuse_reseed11.slurm`; cluster copies under `work/edge_11/`):
- Seeds = 6,593 sparse points inside the face box, per-seed scale log(NN dist), identity rots, opacity init 0.1 — injected via the same `densification_postfix` path as a stock densify step, right after the iter-8000 observe trim, then training continued stock to 30k (seed 22, same config as ticket-03 B_ctrl).
- Re-fusion replicates ticket-03 exactly (stock render.py, full-res, voxel 0.002, 10 clusters, --skip_test, iter 30000) on the reseed model dir.

Reseed marker + kill curve (`B_ctrl_reseed/reseed11_kills.jsonl`, 163 rows; chart `artifacts/edge_11/cover_curve.png`, eyed):
- Iter 8000 trim: face 25,938 before -> 25,764 removed (99.3%) — the wipe reproduced in the reseed run itself.
- Iter 8001 reseed: 6,593 injected, face_after 6,767 (174 survivors + seeds). Iter 9000: face 6,592, all present.
- Iter 9000 trim: 6,589 of 6,592 removed (removed_mean_opacity 0.31, footprint 0.0018). Iter 10000 trim: remaining 6 removed. Face 0 from iter 11000 on; 30k cloud: 0 in box of 627,429 total, 5 within 3fp (frac_of_seeds 0.0).
- The 770-byte face_iter15000.npz is explained (empty face set), not a write bug.

Flat observations (no verdict — numbers for the lead's ruling):
- The seeds survived exactly one trim interval (~1k iters, still present at 9000) and were removed by the very next observe<2 trim — the same rule that killed the originals, not a new failure mode.
- Removed seeds were dim (opacity 0.31) and small (fp 0.0018): consistent with gaussians the face-view cameras never saw as front-visible — i.e. hidden behind existing geometry along those rays — but that mechanism is an inference, not a measurement; the measured fact is observe<2 for all 6,589 within 1k iters of planting.
- With 0 face gaussians at 30k, the pending stock fusion is expected to show a void at the box — mesh confirmation to follow when 33106307 runs.

Files staged (NEW names in `artifacts/edge_11/`, small files only): `cover.json` (curve + snaps + final counts), `cover_curve.png` (eyed). Cluster originals: `work/edge_11/` (kills log, snaps, seeds npz, model dir).

Deviations/limits: (1) pinned-repo `pull --ff-only` NOT run (pre-existing local mods, same as phase A). (2) No LaMa-vs-control claim; mm provisional. (3) Fusion + shaded box render outstanding on GPU queue at write time.

STOPPED — cover verdict staged, mesh evidence pending, no further compute started.

Closing (t11-saver, 2026-10-16, lead ruling: reseed FAILED): fusion job 33106307 CANCELLED by scancel (sacct CANCELLED) — point-cloud evidence sufficient (0/627,429 in box at 30k); a mesh of an empty box would show a void and teach nothing. Final cover: 6,593 seeds in at 8001, 6,592 present at 9000, 0 from 11000 on, 5 within 3fp at 30k. Standing down; ticket resolution and next move are the lead's.
