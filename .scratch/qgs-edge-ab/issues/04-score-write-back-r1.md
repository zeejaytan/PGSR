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

- [ ] Same-ruler relief comparison on the break-face ribbon: QGS vs PGSR-A fraction within ~1 mm (cutoff stated), cross-view depth disagreement in mm for QGS on the same capture, steel remaining in cm² on the QGS mesh
- [ ] QGS-vs-PGSR-A break-face close-ups at ~0.2 mm-resolving scale exist before any score; per-vertex unbinned views where a proxy keeps failing
- [ ] Verdict names which of the three it is (method failed / ruler broken / reference wrong); same-ceiling edge win retires NO per M8's rule with no second seed; a pass scopes the second capture only
- [ ] R1 updated with the date (box ticked, amended, retracted, or retired — uninformative still gets its one line) and the link gate passes
