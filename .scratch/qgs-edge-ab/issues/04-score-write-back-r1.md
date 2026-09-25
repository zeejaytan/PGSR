# 04: Score QGS against PGSR-A on edges and write back to R1

**What to build:** the verdict — QGS scored on break-face relief against the PGSR-A control on the same ruler, drawn before it is numbered, and R1 closed with a date either way.

**Answers:** R1

**Blocked by:** 02 PGSR-A baseline, 03 live QGS run (nothing is scored until both meshes exist with close-ups).

**Status:** ready-for-agent

**Needs-eye:** `visual-qa/preview/qgs_edge_baseline_r1.json` (image close-ups, not a 3D pair — deliberately outside the viewer's `manifest*.json` registry so rescan never tries to stage it) — closes on a witnessed QGS-vs-PGSR-A look plus a conservator note, never on numbers alone.

## Eye 2026-09-21 (single-look QGS viewer, conservator + agent)

- Conservator on the QGS single look (`qgs_A03_single`, staged 2026-09-21 from
  `artifacts/qgs_A03_fuse_post.ply`): **not 10 sherds — rig gone, but most of
  the sherds gone with it.** Agent reply: agreed, and the component audit
  backs the eye exactly (same file, trimesh split, mm via 373.733 sidecar).
- Audit: **107 components**; 10 above 2,000 verts. Component 0 holds **269,261
  verts (46% of the mesh)** spanning **296×438×622 mm** — tray/background
  fused in, not clay. Only components 1, 2, 7, 8 read sherd-scale
  (30–100 mm spans, ~150k verts combined); components 3–6, 9 are elongated
  130–380 mm pieces (rods/walls/backdrop suspects). Control for scale: PGSR-A
  was 10 sherd-scale pieces, 0.0 cm² steel, no background.
- Kind so far: **method-side failure candidate, masking first suspect** — the
  ticket-01 NATIVE GO claim (`use_alpha` + `images_rgba` gates depth at
  fusion) is now suspect: background this large means alpha gating did not
  engage as stated, or engaged on pixels whose alpha the staging didn't
  preserve. Ticket 04 must check whether `gt_alpha_mask` actually gated
  anything (fusion code path + staged alpha audit) before any relief figure —
  a relief score on 4 sherds against a 10-sherd control answers nothing.
## Audit 2026-09-21 (mask seam — the A/B is invalid, QGS is not acquitted)

- Finding: across the whole pinned QGS repo, `gt_alpha_mask` is assigned in
  exactly one place — the `Camera` constructor default `None`
  (`scene/cameras.py:51`). No dataset reader, scene builder, or driver ever
  passes a real mask. The fusion gate
  (`utils/mesh_utils.py:199`: `if mask_backgrond and (... is not None)`)
  therefore **can never fire**. `get_mask()` (the `use_alpha` 4th-band reader
  ticket 01 cited) exists but nothing wires it into the cameras `render.py`
  fuses. Effective config had `use_alpha: true` — a switch connected to
  nothing on the fusion path. The staged RGBA pixels are exonerated (nothing
  reads them at fusion); the ticket-01 NATIVE GO claim is refuted.
- Consequence: the fused mesh ran **fully unmasked** — the 269k-vert
  tray/background component is the predicted result, not a surprise. The
  "same fusion-time masks" premise of the base A/B never held, so this run
  **cannot answer R1 either way**: not a QGS edge verdict, not a ceiling
  verdict — an invalid run. In the workspace's three kinds, this is the
  second: the measurement construction was broken (mask premise false) while
  the method itself stands untested as specified.
- Cheap recovery, no retraining: masking gates fusion only, and both
  checkpoints (7k/30k) are good. The port ticket 01 named but didn't take —
  a PGSR-side extract driver (same precedent as `qgs_run_train.py`) that
  loads the scene, sets each camera's `gt_alpha_mask` from its own
  `get_mask`, then calls `reconstruction()` + `extract_mesh_bounded()` —
  keeps the QGS checkout at pin, reuses the finished 30k model, and costs
  one ~5-minute extraction. R1's pin section is amended from NATIVE GO to
  PORT-required; ticket 01's mask box reopens as PORT.
## Retry 2026-09-21 (PORT driver built, masked extraction submitted)

- Conservator: "let's try again" — approved recovery as proposed (port driver
  + re-extract, no retraining).
- `scripts/qgs_run_extract_masked.py` (new): mirrors `render.py`'s mesh path,
  wires `gt_alpha_mask` from each camera's `get_mask` before
  `reconstruction()`; refuses on non-RGBA pixels, foreground outside
  (0.001, 0.5), mask/depth shape mismatch, config parity drift, or existing
  output. Writes `fuse_masked.ply` (+ `_post`), never touches the unmasked
  pair. `slurm/qgs_extract_masked_a03.slurm` (new): same env/guard/trap
  pattern. Both syntax-checked; QGS checkout untouched at pin.
- Batch **30887248** submitted (scheduler-bumped to gpu-a100 as before).
  Laptop poll watching (1-min interval). On success: fetch
  `fuse_masked_post.ply`, component audit (tray must be gone, sherd count vs
  10), then the 04 scoring seam.
- 30887248 FAILED in 28 s, exit 1 — library load, not science: `import
  sqlite3` (via mediapy→IPython in the `mesh_utils` import chain) picked the
  module stack's GCC 11.3.0 libstdc++ off `LD_LIBRARY_PATH`, which lacks the
  CXXABI the env's own libicu needs. Stock `render.py` survived this on its
  node; the masked driver met a node where it doesn't. Fix committed
  (`fed0e83`): prepend `$ENV_PREFIX/lib` (ships libstdc++ 6.0.36, carries the
  CXXABI) after activation — deterministic on any node. Resubmitted as
  **31200829** with laptop poll (1-min).
- 31200829 FAILED in 4m33s, exit 1 — my own shape guard refused, correctly
  in spirit but wrong in comparison: mask `(1, 2133, 3200)` vs depth
  `(2133, 3200)` differ only by a leading singleton dim the upstream gate
  broadcasts over fine. Positive news inside the failure: reconstruction ran
  all 143 train cameras and the foreground-fraction guard passed, so the
  alpha data is sane. Fix committed (`2a954af`): squeezed shape comparison.
  Resubmitted as **31276616** with laptop poll (1-min).
- Course correction (conservator direction): batch loop abandoned, holder
  31276689 opened (short, CPUS=8 MEM=110G from 30829214's MaxRSS 89 GB).
  In-holder masked extraction COMPLETED — then the IndexError on the
  upstream gate (`depth[mask<0.5]` with (1,H,W) mask vs 2-D depth: dead code
  upstream, never ran with a real mask). Fix committed (`63a59b7`): squeeze
  on attach. Re-ran in-holder → `fuse_masked.ply` written, BUT raw/post
  counts and bounds bit-match the unmasked run except colors — geometry
  identical, so the mask changed nothing fused.
- Why (probed, not guessed): `reconstruction()` ALREADY gates via
  `viewpoint_cam.get_mask` directly (mesh_utils.py:134-135) — the
  `gt_alpha_mask` gate in `extract_mesh_bounded` is a redundant second lock
  with no key upstream. Plumbing verified (`dataset.use_alpha` → cam_info →
  Camera; undistorted pixels RGBA binary alpha). Mask-vs-photo overlay
  (`artifacts/mask_probe.png`): correct — sherds kept, tray cut. Single-view
  depth probe (`scripts/probe_mask_depth.py`): kept 2.0%, gated depths
  2.94–4.44 sane, viz shows clean sherd-shaped gradients.
  Backprojection probe (`scripts/probe_backproject_qgs.py`): masked depths
  land [-0.74..0.54, -0.61..0.70, -0.83..0.42] — on the training points'
  neighborhood. **Depths, masks, extrinsics all acquitted; the curtain is
  built by TSDF from correct inputs, or the model depths disagree across
  views (floaters).** Next: cross-view depth disagreement (already a 04
  scoring item) decides method-vs-integration before any relief figure.
- Verdict 2026-09-25 (cross-view probe `scripts/probe_depth_disagree_qgs.py`,
  12 nearest-neighbour train pairs, 560k shared px, in-holder): disagreement
  **p50 3.96 mm, mean 86.5 mm, p90 345 mm** — pairs range from sub-mm
  (0→29: 0.82; 142→114: 0.20) to whole-scene (129→51: p50 419 mm on 16k px;
  103→79: p50 212 mm). Against the M1 ~1 mm bar the model is
  view-inconsistent by 4× at median and ~90× at mean. This is the curtain's
  mechanism: 143 disagreeing views fused = smeared walls + only the 4
  mutually-agreeing sherds surviving. The authors' own warning (overfitting
  in sparse/low-texture regions) predicted exactly this.
- **R1 verdict: NO — method failed on this material (kind 1 of 3).** Under
  PGSR-identical conditions (same 164 views, full res, 0.75 mm grid, same
  fusion-time masks, one seed, pinned defaults) QGS yields no scorable mesh:
  curtain + 4/10 sherds vs PGSR-A's clean 10. Not the same ceiling — worse:
  no mesh to score relief on. Per R1's gate: retire at one-capture weight,
  no second seed/capture. Tuning (regs/curvature knobs) is out of scope by
  the pin. Holder 31276689 released after the probe (no idle burn).
- Closes on witnessed look + conservator note (this ticket's Needs-eye):
  masked single staged (`qgs_A03_masked_single`), viewer serving; conservator
  confirms the curtain/4-sherd reading on the masked file, verdict ticks R1.
- 2026-09-25 course correction (conservator direction): **batch loop
  abandoned for this step.** Three batch failures in a row, each a seconds-
  to-minutes fault after a queue wait, is exactly the debugging loop the
  held allocation exists for (`docs/agents/slurm.md`) — the lead should have
  switched after the second failure instead of treating each as "one more
  batch". 31276616 cancelled while PENDING (stale poll confirms CANCELLED,
  no work lost). Holder requested on `gpu-a100-short` (CPUS=8, MEM=110G —
  sized from 30829214's measured MaxRSS 89 GB, stays under the ~124G bump
  threshold; 4h hold), step 1 = the masked driver via `gpu_session.sh run`.
  Any further fault gets fixed and retried inside the holder, no requeue.

- [ ] Same-ruler relief comparison on the break-face ribbon: QGS vs PGSR-A fraction within ~1 mm (cutoff stated), cross-view depth disagreement in mm for QGS on the same capture, steel remaining in cm² on the QGS mesh
- [ ] QGS-vs-PGSR-A break-face close-ups at ~0.2 mm-resolving scale exist before any score; per-vertex unbinned views where a proxy keeps failing
- [ ] Verdict names which of the three it is (method failed / ruler broken / reference wrong); same-ceiling edge win retires NO per M8's rule with no second seed; a pass scopes the second capture only
- [ ] R1 updated with the date (box ticked, amended, retracted, or retired — uninformative still gets its one line) and the link gate passes
