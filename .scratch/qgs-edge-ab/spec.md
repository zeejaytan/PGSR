## Problem Statement

**Answers:** R1

PGSR is closed as a sherd mesh route (M8 verdict 2026-09-13: regs catch-22, 0.75 mm grid, variant B OOM ceiling — method failed on this material, type 1). The candidate that could still justify GPU — Quadratic Gaussian Splatting (QGS, `will-zzy/QGS`, arXiv:2411.16392), paraboloid primitives with geodesic density plus curvature-guided normal consistency — currently has no pinned build, no stated mask path, and no PGSR-identical comparison behind it. Without those, a QGS run re-buys the ceiling M8 already measured at higher GPU cost (DTU 48 min vs PGSR 40 min, TNT 75 vs 66, slower FPS).

That placement causes three concrete problems. First, QGS's only distinguishing claim (edges where planar discs over-smooth) is untested on sherd material at the 0.2 mm ridge scale — DTU/TNT/MipNeRF360 are cm-scale clean objects with no clamp rig. Second, QGS fuses via the same Open3D TSDF class that hit the block/OOM ceiling in M8 and regularises via the same homography+NCC multi-view loss that fought chrome highlights in the regs catch-22, so an unscoped trial risks rediscovering both at QGS prices. Third, QGS ships with no mask path, and its authors report overfitting in sparse/low-texture regions with curvature losses unsatisfactory — the rig question that closed M4/M5 is open again for a new build unless the trial states its mask construction before any job.

## Solution

Run one small PGSR-identical A/B and stop there: a pinned QGS build trained once on the existing `A03_sherds` dataset at full capture resolution, extracted at the same voxel size and truncation band in millimetres as the M8 verdict with the same fusion-time masks, scored on break-face relief specifically against the PGSR variant-A mesh as the control (not OpenMVS). Break-face close-ups resolving ~0.2 mm ridges come before any number. If QGS beats PGSR on edges but lands on the same ceiling, that is motion without progress per M8's own rule — retire NO at one-capture weight. A NO costs days, not weeks. No new sibling folder unless the base A/B passes; R1 moves by amendment if it does.

## User Stories

1. As a conservator, I want QGS judged only on the break-face ribbon it must preserve, so that a smooth whole-sherd average cannot pass off a mesh the matcher cannot use.
2. As a conservator, I want break-face relief stated in millimetres with its cutoff (Ra/Rq after the break's own meander is filtered out), so that the edge figure means the same thing as every other relief figure here.
3. As a conservator, I want QGS versus PGSR variant-A close-ups at a view resolving ~0.2 mm ridges before any score, so that a whole-tray view cannot pass off a coarse mesh the way it has before.
4. As a conservator, I want any QGS mesh at true scale or refused, so that a millimetre figure I act on is a millimetre.
5. As a conservator, I want remaining steel stated in square centimetres on the QGS mesh, so that clean is a measurement and not an impression.
6. As a conservator, I want clamp-contact faces written down as unobserved rather than filled in, so that no method invents clay nobody photographed.
7. As a researcher, I want the QGS build pinned by commit hash in R1 before any job, so that the run is repeatable.
8. As a researcher, I want training at full capture resolution with no silent downsample, so that the trial answers the resolution question actually asked.
9. As a researcher, I want the voxel size and truncation band stated in millimetres for the QGS extraction, so that the grid is a claim about sampling, not a hidden coarsening.
10. As a researcher, I want the same 164 `A03_sherds` views M8 used, so that dataset is not the variable.
11. As a researcher, I want the same fusion-time masks as M8 variant A (community alpha construction), so that masking is not the variable.
12. As a researcher, I want the PGSR variant-A mesh named by path as the control, so that "better on edges" is measured against something that exists.
13. As a researcher, I want the mask construction for QGS stated before GPU (native path, ported alpha construction, or declared missing with a NO-GO), so that a variant fed the rig cannot be credited with removing it.
14. As a researcher, I want cross-view depth disagreement in millimetres for QGS on the same capture and ruler, so that the honest resolution floor is measured, not assumed.
15. As a researcher, I want block counts and free-memory figures printed before any QGS extraction, so that a crash at the required voxel is read as the known ceiling, not a new mystery.
16. As a researcher, I want retired lines to stay retired (training-time masking, post-training pruning per M4/M5) without fresh justification, so that two settled NOs are not re-bought at QGS prices.
17. As a researcher, I want curvature-related QGS knobs (`densify_grad_threshold`, `lambda_dist`, `depth_ratio`, curvature losses) recorded at their run values with defaults kept unless stated, so that tuning is not the hidden variable.
18. As a researcher, I want the result written back into R1 with a date either way, so that the question closes even when the answer is uninformative.
19. As a researcher, I want second seeds, second captures, re-photography, tiling builds, and viewing-only scoring out of scope until the base A/B passes, so that a NO stays cheap.

## Implementation Decisions

- Scope is pin plus one-capture verdict, in that order: first the pinned source record exists (QGS commit, control mesh path, dataset provenance, voxel/band in mm, mask construction stated); then the single training plus extraction runs once. No re-photography, no remount; clamp-contact holes stay recorded as unobserved.
- QGS and PGSR sources are treated as distinct builds with separate pins recorded before any submission: QGS commit hash in R1, PGSR variant-A mesh named by path (frame-correct stock-posed mesh under review at `PGSR/artifacts/review_A_stock/`; the Sep-12 fork-posed mesh is INVALID displaced and never a control). An unpinned run is not a result.
- Dataset is fixed: existing `A03_sherds`, same 164 views M8 used, full capture density throughout (`-r 1`; the silent-downsample default stays refused), every-8th-view holdout kept for honest views where the build supports it.
- Extraction parity is fixed: same voxel size and truncation band in millimetres as the M8 verdict (0.75 mm grid stated with route sidecar), same fusion-time masks (variant-A community alpha construction). QGS renders median depth and fuses via Open3D TSDF like PGSR/2DGS — same ceiling class, same reading if it crashes.
- Masking here means fusion-time outlines deciding what counts as clay when depth enters the grid, plus a small-component filter only where stated. QGS has no native mask path on record: the pin ticket states whether the alpha construction ports, is natively supported, or is missing (missing = NO-GO before GPU, not a training run that feeds the rig). Training-time masking and post-training pruning stay retired per M4/M5 and are not relitigated without fresh justification.
- QGS run values are recorded, not tuned silently: `densify_grad_threshold` and `lambda_dist` (primitive count vs compactness), `depth_ratio` (per-pixel resorting removes the 2DGS disk-aliasing block at 1, but the run value is stated), curvature distortion/flatten losses (authors report unsatisfactory — left off unless the pin ticket justifies otherwise). One seed. 30k-iteration class per upstream default unless the pin ticket states otherwise with reason.
- Resolution discipline carries over unchanged: scale anchored per M3 with unscaled results refused rather than measured; `mask_content.py` steel-vs-clay split for the inputs actually used.
- Sequencing inside the trial is fixed: the pin record, then the cheap edge boxes (PGSR variant-A relief baseline + close-ups — the control must exist before QGS burns GPU), then the QGS live run, then scoring + write-back. If the mask construction is missing at pin time, the trial stops there.
- The verdict distinguishes the three failure kinds because they lead to opposite decisions: the method failed on this material, the measurement was broken, or there was never valid material to score against.
- Standing machine rules carry over unchanged: heavy data stays on the cluster, small renders and metrics land in `artifacts/`, no batch submission without explicit approval. Laptop-side poll on every submit per workspace rule 4.
- Cluster env is reuse-first: the MILo env carries most of the stack; QGS needs its own additive rasterizer build (quadric CUDA kernels, distinct from `diff-plane-rasterization`) compiled into it or a stated delta env — no fresh env unless an import probe fails, then only the additive delta.
- R1 stays in `PGSR/intent/` for this trial. A QGS sibling folder (same shape as this one) is earned only by a base A/B pass, and R1 moves there by amendment, never by duplication.

## Testing Decisions

- A good test here compares two meshes against each other on the same capture and the same ruler, never against ground truth (none exists for a Rabati sherd): QGS versus the PGSR variant-A mesh, in millimetres with scale provenance, fraction of break-face ribbon within the ~1 mm requirement as the shared figure. Whole-sherd averages are reported only to show they dilute the edge, never as the verdict figure.
- Seams, in order: the pin seam (commit resolves, dataset provenance present, voxel/band in mm stated, mask construction stated, control mesh path resolves); the control seam (PGSR-A relief baseline + ridge-resolving close-ups exist before QGS trains); the live seam (one full-res training, one same-voxel extraction, block/memory figures printed first); the scoring seam (relief fraction, QGS-vs-PGSR-A close-ups, steel cm², depth disagreement, R1 write-back).
- Modules under test: the QGS training path (full-res pixels in, held-out views honest); the QGS fusion path (rig absent from the fused grid with clay intact at the rim under the stated mask construction); the instrumentation itself (input steel-vs-clay split; relief with cutoff; scale sidecar refuse-not-measure gate that proves it can fail).
- Prior art to follow: the every-Nth-view holdout discipline for honest views; pairing every claim with a figure; gate-style self-checks that prove the instrumentation can fail; the render-before-number rule — no scoring box ticks without close-ups at a scale that resolves the ridge, and per-vertex unbinned views where a proxy picture keeps failing. Tickets carrying close-ups bear a `Needs-eye:` line and close on a witnessed look plus a conservator note, not on numbers.
- Each verdict names which of the three it is — method failed on this material, measurement broken, or reference answer wrong.
- The loop gate runs after ticketing and after close: the link checker must report zero errors, and any resolved ticket must have moved R1.

## Out of Scope

- Second seeds, second captures, re-photography, remounting, or lighting changes.
- Tiling or chunked-extraction builds before the base A/B reports; if QGS hits the block/OOM ceiling at the required voxel, R1 is amended to the tiling question rather than built around silently.
- Re-animating training-time masking or post-training pruning under QGS (retired under M4/M5; fresh justification required).
- Viewing-only scoring (fast novel views judged on renders, never in millimetres) unless the base mesh A/B passes.
- OpenMVS as the control — PGSR variant A is the control; OpenMVS already has its ceiling role in M8.
- Point-cloud meshing across occlusion holes that invents unphotographed surface; worse than a hole for a conservation record.
- A new QGS sibling folder, new remotes, or Spartan paths before the base A/B passes.
- Any chapter-level method-list decision (that belongs to the cross-project comparison question; this spec only produces the numbers it will need).

## Further Notes

- Answers R1; triage state for the tickets is ready-for-agent once cut. Vocabulary follows the glossary: `CONTEXT.md` fixes "edge" as break-face relief (Ra/Rq + cutoff), never rim silhouette or render crispness.
- QGS sources: paper arXiv:2411.16392 §§3.2–3.3 (paraboloids, geodesic density, ray-quadric intersection, curvature-guided normal consistency Eq. 17), §4.1 (median-depth + Open3D TSDF, voxel 0.004 / trunc 0.02 in benchmark units), §4.2–4.3 (DTU CD 0.54 vs PGSR 0.56; disabling curvature guidance fills fine gaps); repo `will-zzy/QGS` README (no mask path; curvature losses unsatisfactory; `densify_grad_threshold` / `lambda_dist` / `depth_ratio` knobs; slower train/FPS than 2DGS; 3 open issues incl. late-training NaNs).
- M8 is answered NO (regs catch-22 causal 7k test, 0.75 mm grid, B OOM ceiling); R1 is the follow-on with PGSR-A as control. M1 (~1 mm requirement) and M3 (true scale) still frame the bars.
- Next step is the ticket breakdown below, then the link gate.
