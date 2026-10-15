# 11: Save the face blobs — diagnose steel-vs-sunk, then intervene

**What to build:** the retry, in two gated phases. Ticket 10 named the killer (observe<2 trim, 99.86% at iter 8000) and the lead's follow-up showed the flag counts front-visible contributors only. What it did NOT settle: are the true face-surface blobs steel-blocked in the views that matter, or sunk inside the clay? The fix differs, so phase A diagnoses, the lead picks, phase B intervenes.

**Answers:** R2

**Blocked by:** none (conservator chose diagnose-then-fix 2026-10-15).

**Status:** in-progress
**Working in:** teammate t11-saver, phase A steel-vs-sunk only (2026-10-15); phase-B retrain waits for lead pick

- [ ] Phase A — steel-vs-sunk (CPU only): project the ticket-10 face-box region through the train cameras view by view; for each view, is clamp steel in front of the face surface (use masks + rendered depths from the ticket-03 scenes)? Report per-view front-blocked fractions + pictured overlays. Verdict reserved to the lead: STOP after staging and report.
- [ ] GATE: lead picks the matched fix — (1) face-box exemption from the trim if steel-blocked, (2) post-wipe reseed + continued training if sunk-inside, (3) rule relaxation only if the evidence forces it. No GPU retrain starts before the pick.
- [ ] Phase B — intervene per the pick (GPU retrain, one arm first): copy-trainer discipline (never edit pinned files), same seed/config as ticket 03, new out dir, polled, sacct recorded. Then re-fuse at the stock grid and render the face box: does a surface exist now?
- [ ] Restraint: no LaMa-vs-control claim until a surface exists in at least one arm; small files to `artifacts/edge_11/`; work-notes only, never commits.

**Rules carried over:** renders before numbers; mm provisional; heavy compute on Spartan only.
