# 11: Save the face blobs — diagnose steel-vs-sunk, then intervene

**What to build:** the retry, in two gated phases. Ticket 10 named the killer (observe<2 trim, 99.86% at iter 8000) and the lead's follow-up showed the flag counts front-visible contributors only. What it did NOT settle: are the true face-surface blobs steel-blocked in the views that matter, or sunk inside the clay? The fix differs, so phase A diagnoses, the lead picks, phase B intervenes.

**Answers:** R2

**Blocked by:** none (conservator chose diagnose-then-fix 2026-10-15).

**Status:** in-progress
**Working in:** teammate t11-saver, phase B reseed retrain on B_ctrl (2026-10-15); surface check returns for lead ruling

**Gate pick (lead, 2026-10-15, overlay + chart eyed):** NOT steel-blocked — 1101–1105 zero steel-on-face, priority views ≥98% clear, yet the global wipe still took 99.86%. The blobs sank inside. Exemption parked; reseed picked: re-plant at the 6,593 measured SfM face-seed positions right after the iter-8000 wipe, continue to 30k, re-fuse stock grid, render the box. One arm (B_ctrl) proves mechanism; A/B comparison waits for a surface in at least one arm.

- [ ] Phase A — steel-vs-sunk (CPU only): project the ticket-10 face-box region through the train cameras view by view; for each view, is clamp steel in front of the face surface (use masks + rendered depths from the ticket-03 scenes)? Report per-view front-blocked fractions + pictured overlays. Verdict reserved to the lead: STOP after staging and report.
- [ ] GATE: lead picks the matched fix — (1) face-box exemption from the trim if steel-blocked, (2) post-wipe reseed + continued training if sunk-inside, (3) rule relaxation only if the evidence forces it. No GPU retrain starts before the pick.
- [ ] Phase B — intervene per the pick (GPU retrain, one arm first): copy-trainer discipline (never edit pinned files), same seed/config as ticket 03, new out dir, polled, sacct recorded. Then re-fuse at the stock grid and render the face box: does a surface exist now?
- [ ] Restraint: no LaMa-vs-control claim until a surface exists in at least one arm; small files to `artifacts/edge_11/`; work-notes only, never commits.

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
