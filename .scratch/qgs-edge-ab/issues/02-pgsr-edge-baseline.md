# 02: PGSR-A break-face edge baseline before QGS trains

**What to build:** the control, measured and drawn — PGSR variant-A break-face relief baseline with ridge-resolving close-ups, so QGS has something real to beat and no GPU is spent before the ruler exists.

**Answers:** R1

**Blocked by:** 01 pin QGS source (voxel/band in mm and mask construction must be stated first, or the baseline measures the wrong grid).

**Status:** resolved

**Needs-eye:** `visual-qa/preview/qgs_edge_baseline_r1.json` (image close-ups, not a 3D pair — deliberately outside the viewer's `manifest*.json` registry so rescan never tries to stage it) — closes on a witnessed look plus a conservator note, never on numbers alone.

- [x] Break-face relief for the PGSR-A control on A03: method-local Rq-like character at stated scale (see Answer) — ribbon-rim zones, whole-sherd averages shown only in stats.json
- [x] QGS-vs-PGSR-A close-up views staged at a scale resolving ~0.2 mm ridges before any score; whole-tray views alone do not pass (PGSR-A side staged; QGS side lands in 04)
- [x] Scale sidecar per M3 (373.733 mm/unit, refuse-not-measure gate intact — script exits 1 on unreadable/empty input) and rig check: input split per `provenance_A03.json` (alpha mean ~2.3%) plus remaining steel in cm² on the control mesh (see Answer)
- [x] Clamp-contact faces recorded as unobserved, never filled (see Answer)
- [ ] Pass/fail fraction within ~1 mm — AMENDED to 04 with reason (see Answer): no reference surface exists for a single mesh, so a "fraction within" figure needs both meshes.

## Answer 2026-09-13 (measured; eye pending)

Control: `PGSR/artifacts/review_A_stock/tsdf_fusion_post.ply` via `scripts/measure_edge_baseline.py` → `artifacts/edge_baseline_02/` (stats.json, relief_hist.png, closeup_0/1.png, context.png). Reproduced M8's inventory exactly (96,719 verts / 173,900 faces / 10 pieces) and put millimetres on it.

- **Grid-limited, as M8 said:** median triangle edge **0.77 mm** (p10 0.23, p90 1.06) — the mesh IS the 0.75 mm grid. Nothing below ~1.5 mm in it is honest surface.
- **Relief character (R = 1.5 mm ball, n = 5,974, plane-fit RMS):** p10 0.16 / p50 **0.35** / p90 0.49 mm. Method-local Rq-like figure — same code and R will run on the QGS mesh in 04, so the comparison is like-for-like. It is NOT an ISO profile Ra (no meander filtering); the ticket checkbox was met in that stated sense.
- **Close-ups (viewed by agent 2026-09-13):** 15 mm rim crop at the highest-relief rim vertex of the largest piece. Reads as coarse grid lumps with visible fusion holes, not crisp clay — facet scale ~0.5–1 mm, no 0.2 mm structure present (cannot be, at this grid). This picture is the bar QGS must beat.
- **Steel 0.0 cm² by component audit:** all 10 components sherd-scale (spans 18–81 mm, areas 2,100–6,300 mm²); no rod/plane rig outliers. Eye-confirmed on renders (no chrome shapes; holes read as missing surface, not steel).
- **Clamp-contact:** recorded unobserved — fusion-masked build excludes unphotographed contact faces by construction; small white gaps in the close-ups are missing surface, never filled.
- **Kind so far:** measurement, not verdict — no method/ruler/reference claim attaches to the control alone. R1 boxes stay unticked until 04 scores both meshes.

## Eye 2026-09-13

Conservator looked at the rim close-ups: reads as coarse blocks, edge detail not cleanly legible at this grid. Agent reply: agreed — that is exactly the bar finding (0.77 mm median edges cannot carry 0.2 mm ridges); QGS must beat this picture in 04. Eye closes the PGSR-A side; QGS side stages in 04.
