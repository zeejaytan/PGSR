# 10: Trace which prune rule kills the face cover during training

**What to build:** the open seam from ticket 07 — instrument ONE training run and watch the face-box cover die: which rule, at which iteration, under what stats. No fix in this ticket; the intervention is ticketed after, against the named rule.

**Answers:** R2

**Blocked by:** none (conservator chose trace-first 2026-10-15).

**Status:** resolved

## Answer (lead ruling 2026-10-15, kill table + cover curve eyed — proposal ACCEPTED)

The killer is the **multi-view observe<2 trim** (`train.py:374-383`): small escalating bites from iter 1000, then one 99.86% blow at iter 8000 (30,959/31,002, removed mean opacity 0.74 — established points). The curve shows climb → vertical wipe → flatline; cover never recovers because growth acts only on existing points. Acquitted: screen-size prune (zero face kills), opacity cull (1,392 weak/newborn only), resets (non-lethal). Run-to-run wobble (764,889 vs 631,016 totals) noted, mechanism structural. Open seam, one level down: WHY 31k high-opacity face points register <2 observations despite 19 constraining views — jaw occlusion, interior scatter, or the rasterizer's observe flag; ticket 11's intervention must answer or route around it.

- [x] Instrument the pinned trainer (ticket-local copies, additions-only diff, pinned files pristine): per-step per-rule face-box kill log with stats at removal.
- [x] Run ONE arm only: B_ctrl, same seed/config, NEW out dir `work/edge_10/B_ctrl_trace/` — 32995950 COMPLETED 0:0 (~2h41), polled.
- [x] Report: 162-row kill table + cover curve (climb → wipe at 8000 → flatline) + 4 face snaps. Named rule: observe<2 trim.
- [ ] Restraint: one arm, one run; no densification change, no LaMa-vs-control claim; small files to `artifacts/edge_10/`.

## Worker work-notes (t10-tracer, 2026-10-15)

Job receipts (sacct JobID|JobName|State|ExitCode|Start|End):
- 32991026|pgsr-smoke10|COMPLETED|0:0 (6-iter GPU smoke of the instrumentation; trace rows + snapshots verified before the real submit)
- 32995950|pgsr-trace10|COMPLETED|0:0|2026-10-15T04:24|2026-10-15T07:05 (~2h41, same pace as ticket 03)
- 33011565|pgsr-rep10|COMPLETED|0:0|2026-10-15T07:09:34|2026-10-15T07:09:42 (sapphire CPU report)
Laptop-side poll on every submit; sacct State/ExitCode recorded.

Instrumentation + pristine-pin check (acceptance a): ticket-local COPIES only — `scripts/trace10/scene/` (full scene package, only `gaussian_model.py` instrumented) + `scripts/trace10/train_trace10.py`; diff vs pinned originals is additions-only (gaussian_model +95/-1: trace block + `trace_iter` kwarg; train +59/-2: pass-through + trim/reset logging + snapshots). Training numerics, seed 22, args, schedule UNCHANGED. Pinned repo HEAD `de24f1a`; `git diff --name-only HEAD -- scene/gaussian_model.py train.py arguments/__init__.py` EMPTY (slurm-side gate re-checked before launch). Pre-existing repo state noted, not mine: `render.py` +8 comment-only lines (the withdrawn-invert note) + staged script/slurm additions; my files never entered the repo (all under `work/edge_10/`). One arm (B_ctrl `data/17062025/A31_control`, `-i images -r 1 --eval`), one run, NEW out dir `work/edge_10/B_ctrl_trace/` (ticket-03 scenes untouched). Never committed/pushed.

Per-rule kill table, 162 rows = 144 densify steps (600–14900) + 14 observe-trims (1000–14000) + 4 opacity resets (3000–12000); totals over the run:
- births into box: 37,209 | opacity-cull kills: 1,392 (removed mean opacity 0.0041, just under the 0.005 line — weak/newborn points) | screen-size-prune kills: 0 | both-rules: 0 | observe<2-trim kills: 36,927
- iters 600–7000: cover climbs 1.8k→5k (births ~130–170/step beat trims 279→1164 + single-digit culls); iters 7100–8000: densification explodes (scene 276k→4.28M via the abs-split path, face 5k→31k); iter-8000 trim takes 30,959/31,002 (99.86%, removed mean opacity 0.74 — established points, not wisps); after: 39–70, never recovers (growth acts only on existing points), 15 at 14900, 13 centres / cover3 26 at 30k (`validation.json`).
- opacity resets move face mean opacity but remove nothing directly. Screen-size prune (20px post-3000) never takes a single face point.
- run-to-run note: trace total 764,889 vs ticket-03 B 631,016; face 13 vs 0 — same starvation order, GPU nondeterminism across nodes; the killing mechanism is structural, not seed luck.
Curve + renders (acceptance c, eyed): `artifacts/edge_10/cover_curve.png` (climb → vertical wipe at 8000 → flatline; densify-prune kills invisible ≈ 0), `face_snap_07000.png` (3,997 centres, structured sheet in box), `face_snap_15000.png` (15 lonely points of 764,889), plus snaps at 500/3000 and `kill_table.json` + `validation.json` in the same dir. Cluster originals: `work/edge_10/report/`; run outputs: `work/edge_10/B_ctrl_trace/` (`trace10_kills.jsonl`, `trace10_snaps/`, both PLYs, instrumented-source copies).

PROPOSAL for the lead's Answer (acceptance d): the killer is the **multi-view observe<2 trim (`train.py:374-383**) — small escalating bites (279→1164) then one 99.86% blow at iter 8000; opacity cull is minor (weak points only), screen-size prune is acquitted (zero), resets are non-lethal. Open sub-question beyond this ticket: WHY 31k high-opacity face points register <2 observations despite 19 constraining views (jaw occlusion? interior scatter? rasterizer observe flag?) — not answered here. Zero fixes (acceptance e); no LaMa-vs-control claim anywhere.

**Rules carried over:** worker appends work-notes only, never commits; GPU batch under standing sign-off with laptop-side poll; renders before numbers where load-bearing.
