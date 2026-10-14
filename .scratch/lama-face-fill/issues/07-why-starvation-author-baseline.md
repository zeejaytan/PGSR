# 07: Why does the face starve — and what did the authors test on?

**What to build:** the reason behind ticket 06's cause, plus an external baseline. Ticket 06 proved *that* training deposits no Gaussians at the face; it did not say *why* densification avoids it, nor whether the authors' own results cover anything like our case. This ticket answers both or reports honestly that it cannot.

**Answers:** R2

**Blocked by:** none (paper texts + pinned repo + our logs exist).

**Status:** resolved

## Answer (lead ruling 2026-10-14, work-notes + seed chart eyed — report ACCEPTED)

Reason hunt ends one level deeper with two candidates dead and one left standing. DEAD: sparse SfM seeds (6,593 sit exactly at the face box vs ~0 beside it — chart eyed) and low image gradients (face bbox is the highest-energy region in frame, 31.8–40.3 vs ~21.4–22.2). So the cover is seeded and signalled, yet gone by iter 30k — the clearing happens DURING training, between iters 500–15,000, by a prune rule this ticket does not identify (opacity cull, post-3000 screen-size prune, observe<2 trim, and 3000-step opacity resets are all suspects; answering needs training-time traces). Baseline: DTU object scans are the nearest author reference (same mm ruler); explicit domain gap — no clamp-held small-face case in the paper, whose own limitation covers missing-viewpoint regions. Read our result as "same ruler, harder case." Retry direction from 06 stands (face-targeted densification + retrain); the trace question is a possible future ticket, not this one.

- [x] Author baseline: 15 DTU object scans (mm chamfer) + 6 metre-scale TnT scenes; Mip-NeRF360 rendering-only. Nothing sherd-scale/occluded — domain gap stated with quotes.
- [x] Pinned-code densification audit: full rules quoted (grad 0.0002/abs-grad 0.0008, interval 100, iters 500–15k, opacity reset 0.01/3000, cull 0.005, 20px post-3000 prune, observe<2 trim); growth acts only on existing points.
- [x] Reason hypothesis with evidence: seed-sparsity and low-gradient candidates both DEAD on our data; clearing happens during training by an unidentified prune rule (needs traces).
- [x] Baseline proposal: DTU as nearest reference; domain gap explicit — no clamp-held small-face author case.
- [x] No fix built here; no LaMa-vs-control claim; pictures carried the load-bearing points.

**Rules carried over:** worker appends work-notes only, never commits; small files to `artifacts/edge_07/`; paper claims carry quotes with file + section.

## Worker work-notes (t07b-baseliner, 2026-10-14 — REBUILD; first lane left nothing)

Remains check (acceptance a): previous lane t07-baseliner left zero verified leavings — `C:\PR\PGSR\artifacts\edge_07/` did not exist on the laptop, `/data/gpfs/projects/punim2657/PGSR/work/edge_07/` does not exist on Spartan (only edge_04/04b/04c/04d/04_raw/06/AB), and this ticket file had no work-notes beyond the template. Everything below is fresh work; nothing reused.

Job receipts (sacct JobID|JobName|State|ExitCode|Start|End; sapphire CPU-only):
- 32980063|pgsr-rea07|COMPLETED|0:0|2026-10-14T22:04:30|2026-10-14T22:04:48 (reason test; `slurm/pgsr_diag07_reason.slurm`)

Staged files (all new, uncommitted; laptop is source of truth, scp'd individually to Spartan; remote py_compile verified before submit): `scripts/diag_reason_07.py`, `slurm/pgsr_diag07_reason.slurm`. Cluster `work/edge_07/reason/` (reason.json + 3 PNGs). Laptop `artifacts/edge_07/` (NEW dir): `pgsr-2406.06521v2.md` (paper text, see deviation), `reason.json`, `seed_counts.png`, `grad_A31_1114.png`, `grad_A31_1115.png` — PNGs + KB JSONs + paper text only. No LaMa-vs-control claim anywhere below.

Deviation: the PGSR paper was NOT in the `C:\PR\papers\text\` corpus (no PGSR row in `catalogue.md`), so I fetched it with the corpus converter (`papers/scripts/convert.py 2406.06521 pgsr` with the papers venv) and moved the result into `artifacts/edge_07/` as ticket evidence instead of leaving it in `text/` — leaving it there would trip the papers `check.py` gate (`text/<name>: no line in catalogue.md`). Verified papers gate still green (`ok: 22 papers`) and `text/` holds no pgsr file. All paper quotes below cite `artifacts/edge_07/pgsr-2406.06521v2.md` with line + section.

Pinned-code check: Spartan repo HEAD `de24f1a`; `git diff --name-only` shows only a build artifact (`submodules/diff-plane-rasterization/.../PKG-INFO`) — `scene/gaussian_model.py`, `train.py`, `arguments/__init__.py` are pristine, so the laptop file+line quotes below apply to the pinned version. A31 trainings ran stock (`train.py -s <arm> -m <out> -i images -r 1 --eval`, jobs 32864742/32864743 per ticket 03); both `output/.../cfg_args` show no densify overrides, so OptimizationParams defaults applied to both arms.

### Author baseline (acceptance b) — quotes from `artifacts/edge_07/pgsr-2406.06521v2.md`

- Testbed (V Experiments, :233): "We chose the widely used MiP-NeRF360 dataset [2] for evaluating novel view synthesis performance. The large and complex scenes of the TnT [28] and 15 object-centric scenes of the DTU dataset [23] were selected to assess reconstruction quality."
- Reconstruction scenes are (V-B, :243-253 Table III) six TnT scenes — Barn, Caterpillar, Courthouse, Ignatius, Meetingroom, Truck (F1 scores, e.g. PGSR Barn 0.66, Ignatius 0.81, Meetingroom 0.33) — plus 15 DTU object-centric scans (chamfer mm, :220-229 Table II, PGSR mean 0.52mm, 0.5h). Mip-NeRF360 is used for novel-view rendering only (:239-241), not surface scoring.
- Scales: TnT = "large and complex scenes" (buildings, a truck, a statue — metre scale); DTU = "object-centric" tabletop scans (roughly 10–20 cm objects, scored in mm). Training is 30,000 iterations, AbsGS densification (:237): "The training iterations for all scenes are set to 30,000. ... We adopt the densification strategy of AbsGS [66]."
- No sherd-scale / clamp-occluded case appears anywhere in the text: no small fragments, no occluders, no thin faces; the only occlusion discussion is pixel-weighting inside multi-view regularization (:171) and the authors' own limitation (:297): "we cannot perform geometric reconstruction in regions with missing or limited viewpoints, leading to incomplete or less accurate geometry." Related observation, quoted without applying it: single-view regularization "tends to create holes on highly specular metallic objects" (supplement, :326) — the clamp jaws at our face are steel.

### Pinned-code densification audit (acceptance c) — file + line

Defaults (`arguments/__init__.py`): `percent_dense = 0.001` (:88); `densification_interval = 100` (:90), `opacity_reset_interval = 3000` (:91), `densify_from_iter = 500` (:92), `densify_until_iter = 15_000` (:93), `densify_grad_threshold = 0.0002` (:94); `use_multi_view_trim = True` (:103); `opacity_cull_threshold = 0.005` (:112), `densify_abs_grad_threshold = 0.0008` (:113), `abs_split_radii2D_threshold = 20` (:114), `max_abs_split_points = 50_000` (:115), `max_all_points = 6000_000` (:116).
Loop (`train.py`): stats accumulate every iter below 15k (:361-366, `add_densification_stats` on `visibility_filter`); `densify_and_prune(grad 0.0002, abs-grad 0.0008, cull 0.005, extent, size_threshold)` every 100 iters after iter 500 (:368-371), with `size_threshold = 20` once past iter 3000 (:369); multi-view trim prunes Gaussians seen in fewer than 2 views (`observe_the = 2`, :374-383); opacity reset clamps everything to 0.01 every 3000 iters (`gaussian_model.py:268-271` `reset_opacity`).
Rules (`scene/gaussian_model.py`): clone needs mean view-space grad ≥ threshold AND small size (`max(scaling) <= 0.001*extent`, :465-470); split needs grad ≥ threshold AND large size (`> 0.001*extent`, :425-427), plus an abs-grad path needing screen radius > 20px (:437-445); prune deletes opacity < 0.005, and after iter 3000 also screen-radius > 20px or world-size > 0.1*extent (:498-514). Growth acts ONLY on existing points — nothing is seeded in empty space.

### Reason test (acceptance d) — `reason.json` + pictured files, flat observations

- Test A (SfM seeds, control sparse, 49,936 points): face box holds **6,593** seeds; same-size neighbours hold 0/0/4/36/3/8; nearest seed 0.0086 units (~3.2 prov-mm) from centroid. Eye on `seed_counts.png`: the face bar dwarfs all neighbours. The "SfM seed sparse at the face" candidate is OUT — seeds concentrate exactly at the sherd.
- Test B (Sobel energy, control images, 6 train face views): face-core means 23.0–67.7, full-bbox 31.8–40.3, rest-of-frame ~21.4–22.2 in every view (full table in `reason.json`). Eye on `grad_A31_1114.png` (+1115): hot edge energy along sherd outlines and jaw steel inside the bbox; the clay interior itself is smooth but the box as a whole is the highest-energy region in the frame. The "plain wall → no densify signal" candidate as stated is OUT at box scale.
- Untested, left open (no claim): which pruning rule removes the seeded face cover between iter 500–15,000 (opacity cull 0.005, post-3000 screen-size prune at 20px, observe<2 trim, 3000-step opacity resets) — answering that needs training-time traces, not built here.

### Baseline proposal (acceptance e)

Closest author-tested reference point: the **DTU object-centric scans** (Table II, chamfer in mm) — the only author case near our physical scale. Explicit domain-gap statement: **no comparable author case exists** for a centimetre-scale, partly clamp-held face — all author reconstruction scenes are fully visible objects/rooms/vehicles, and the paper's own limitation covers missing-viewpoint regions. Read our result against DTU as "same ruler, harder case", not as a defect claim.

### Receipts (acceptance f) / restraint (acceptance g)

Sacct line, file lists, paper-fetch deviation, and pinned-version check are recorded above. No verdicts, no fixes, no LaMa-vs-control claim in this report; the checkboxes and any ruling stay with the lead.
