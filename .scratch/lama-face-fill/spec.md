## Problem Statement

**Answers:** R2

Masked training drains the clay it is meant to clean (M5 on A03: 222,678 → 18,443 Gaussians, ~91% fewer; 2.6M → 276k vertices, eye-confirmed coarser), because the background loss pushes masked-rim opacity to zero, pruning deletes it, and densification has no reason to put clay back. Fusion-time masking avoids the drain but lands on a 0.75 mm grid where 1 mm relief is ~1.3 voxels and 0.2 mm ridges are unresolvable by construction (M8). The clamp covers face only, never the break, so a face fill cannot fake a join — but no fill has been shown to return density as clay rather than as smooth fake, and any break movement is contamination, not success. GScream and InFusion are recorded backups, untested; ReconSplat is out (rooms prior, 256px, no mask input, no metric output).

That placement causes three concrete problems. First, the trial must separate *density* (sampling rate: counts, spacing, footprint) from *detail* (real relief): a smooth blob sampled finely is still a blob, and vertex spacing alone has already hidden a failure here once. Second, pixels grown from LaMa texture are inferred everywhere they constrain — if the generated flag cannot be honoured downstream, the dense mesh is not a record mesh regardless of counts. Third, the LaMa arm trains on altered photographs, so the break-face arc must be shown unmoved in millimetres, not assumed from the clamp sitting on the face.

## Solution

Run one small A/B and stop there: one sherd, one seed, same views — arm A trains on LaMa-inpainted inputs (clamp/rig pixels filled at full photo resolution, no training mask, no background loss), arm B is the unmasked control. Score density recovery (counts, spacing, footprint) against break stability (arc agreement in mm), flat-wall noise (mm), a held-out known face patch (mm deviation), and a PLY generated-flag the matcher demonstrably ignores, with ridge-resolving renders before any number. If density returns as clay with the break untouched and the flag honoured, scope the second sherd and the GScream/InFusion comparison. A NO costs days, not weeks.

## User Stories

1. As a conservator, I want density reported as counts and spacing and detail reported as relief in millimetres separately, so that a finely-sampled smooth fake cannot pass as recovered clay.
2. As a conservator, I want break-face arc agreement in millimetres on sampled edges, so that any break movement reads as contamination, not success.
3. As a conservator, I want flat-wall noise in millimetres on quiet faces, so that roughening from fake texture is measured, not eyeballed.
4. As a conservator, I want a held-out known face patch generated and compared to its true surface in millimetres, so that the fill is judged against an answer key before it touches clamp holes.
5. As a conservator, I want generated vs measured flagged in the PLY and honoured by the matcher, so that no downstream join ever treats invention as evidence.
6. As a conservator, I want rim/face close-ups at a view resolving ~0.2 mm ridges before any score, so that a whole-sherd view cannot pass off a coarse mesh the way it has before.
7. As a conservator, I want clamp-contact faces that no view ever saw left as recorded holes, so that the fill covers clamp-visible-elsewhere pixels, never the permanently unobserved jaw contact.
8. As a researcher, I want the LaMa build pinned by commit hash with weights named before any job, so that the inpaint is repeatable.
9. As a researcher, I want the inpaint mask construction stated (which pixels, dilated by how much, propagated across views how), so that mask is not the hidden variable.
10. As a researcher, I want identical seed, config, and iteration count across arms, so that dataset and schedule are not the variables.
11. As a researcher, I want full capture resolution throughout with no silent downsample, so that the trial answers the resolution question actually asked.
12. As a researcher, I want the same views for both arms with every-8th-view holdout kept, so that held-out views stay the honest instrument.
13. As a researcher, I want Gaussian counts, mesh vertex counts, and kept-Gaussian footprint (median/p90 in mm) stated for both arms, so that density recovery is a measurement.
14. As a researcher, I want the extraction voxel size and truncation band stated in millimetres for both arms, so that the grid is a claim about sampling, not a hidden coarsening.
15. As a researcher, I want scale anchored with unscaled results refused rather than measured, so that a millimetre figure acted on is a millimetre.
16. As a researcher, I want the flag-exclusion demonstrated (matcher fed the flagged mesh, generated vertices provably unused), so that the label is a mechanism, not paint.
17. As a researcher, I want M5's construction to stay closed (no background-loss + pruning arm), so that a settled NO is not re-bought — the LaMa arm trains mask-free on filled inputs.
18. As a researcher, I want GScream/InFusion to stay parked until this A/B reports, so that backups are not built in parallel with the baseline.
19. As a researcher, I want the result written back into R2 with a date either way, so that the question closes even when the answer is uninformative.
20. As a researcher, I want second seeds, second sherds, and re-photography out of scope until the base A/B passes, so that a NO stays cheap.

## Implementation Decisions

- Scope is pin plus one-sherd A/B, in that order: first the pinned source record exists (LaMa commit + weights, control inputs provenance, mask construction, voxel/band in mm); then the single inpaint plus two trainings plus extractions run once. No remount; jaw-contact holes stay recorded as unobserved.
- The LaMa arm alters photographs, not the loss: inpainted inputs train mask-free with the production loss untouched, so M5's both-sides-plus-alpha verdict is not relitigated — a different arm with a different mechanism.
- The inpaint mask covers clamp/rig pixels only, with dilation and cross-view propagation stated at pin time; break pixels are never inpainted, and the jaw-contact region (unseen in all views) is excluded from fill and from scoring as damage.
- Density and detail are scored as separate quantities with separate instruments: counts/spacing/footprint for density; relief-with-cutoff, arc agreement, and wall noise for detail. No single figure is allowed to stand for both.
- The generated flag is a per-vertex (or per-component) attribute written at mesh build time, with a named consumer contract: placement/matching stages exclude flagged vertices, demonstrated by a run that proves exclusion, not by documentation.
- Sequencing inside the trial is fixed: pin record, then inpaint + held-out-patch check (the fill must track known skin before it touches clamp holes), then the two trainings, then extractions at the stated voxel, then scoring + eye + write-back. If the held-out patch misses by more than the face tolerance, the trial stops before scoring clamp holes.
- Standing machine rules carry over unchanged: heavy data stays on the cluster, small renders and metrics land in the landing zone, laptop-side poll on every submit.
- Compute env is reuse-first: use an existing Spartan conda env that already carries the dependency wherever possible (the MILo env carries the Python/CUDA stack; LaMa needs only an additive install into it), and build a fresh env only if an import probe fails — then only the additive delta, recorded at pin time.
- R2 stays in the PGSR intent folder for this trial. A GScream/InFusion comparison is earned only by a base A/B pass, and is ticketed separately, never folded silently into this A/B.

## Testing Decisions

- A good test here compares two meshes from two input sets on the same sherd and the same ruler, never against ground truth (none exists for a Rabati sherd): LaMa arm versus unmasked control, in millimetres with scale provenance. Whole-mesh averages are reported only to show they dilute the face, never as the verdict figure.
- Seams, in order — confirm these match your expectation before ticketing:
  1. the pin seam (LaMa commit + weights resolve, mask construction stated, voxel/band in mm stated, control inputs named);
  2. the inpaint seam (held-out known patch fills within face tolerance before clamp pixels are touched);
  3. the training seam (identical seed/config/iterations, full resolution, holdout kept, counts + footprints recorded);
  4. the scoring seam (arc agreement, wall noise, patch deviation, flag-exclusion run, R2 write-back);
  5. the eye seam (ridge-resolving close-ups witnessed with a conservator note, closing on the look plus the note, never numbers alone).
- Modules under test: the inpaint path (full-res pixels in, break pixels excluded, jaw contact excluded); the training path (density response to filled inputs); the flag path (generated attribute written and honoured downstream); the instrumentation itself (relief with cutoff, scale refuse-not-measure gate that proves it can fail).
- Prior art to follow: the every-Nth-view holdout discipline for honest views; pairing every claim with a figure; gate-style self-checks that prove the instrumentation can fail; the render-before-number rule — no scoring box ticks without close-ups at a scale that resolves the ridge, and per-vertex unbinned views where a proxy picture keeps failing. Tickets carrying close-ups bear a `Needs-eye:` line and close on a witnessed look plus a conservator note, not on numbers.
- Each verdict names which of the three it is — method failed on this material, measurement broken, or reference answer wrong.
- The loop gate runs after ticketing and after close: the link checker must report zero errors, and any resolved ticket must have moved R2.

## Out of Scope

- Second seeds, second sherds, second captures, re-photography, remounting, or lighting changes.
- GScream / InFusion builds before the base A/B reports; if LaMa passes, they are ticketed separately against the LaMa mesh as control.
- ReconSplat in any form (rooms prior, fixed low resolution, no mask input, normalised depth — out on mechanism, not on tuning).
- Re-animating M5's background-loss construction or M4's post-training pruning (both retired; fresh justification required).
- Inpainting break pixels under any circumstance; filling jaw-contact regions no view ever saw.
- Tiling or chunked-extraction builds before the base A/B reports; if extraction hits the block/OOM ceiling at the required voxel, R2 is amended to the tiling question rather than built around silently.
- Any chapter-level method-list decision (that belongs to the cross-project comparison question; this spec only produces the numbers it will need).

## Further Notes

- Answers R2; triage state for the tickets is ready-for-agent once cut. Vocabulary follows the glossary: relief is Ra/Rq height in mm after the break's own meander is filtered out with cutoff stated; point spacing is the step size of the measurement, never a bump height.
- Sources: M5 verdict 2026-09-06 (222,678 → 18,443 Gaussians, 276k vs 2.6M verts); M8 verdict 2026-09-13 (0.75 mm grid, variant B OOM); R1 control (PGSR-A 96,719 verts, 0.77 mm median edge); U14 (labelled completion gate); LaMa repo (full-res fully-convolutional inpainting) + Marigold/MiDaS-style aligned depth as the fusion companion, exact pins at ticket time.
- Next step is the ticket breakdown below, then the link gate.
