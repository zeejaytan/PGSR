# 06: Diagnose why the A31 face fuses to fragments

**What to build:** the mechanism, not a fix. Ticket 04 proved *that* the sherd region fuses to scattered slivers (raw) and a hole (post) in both arms at the stock grid — this ticket finds *why*, with pictured evidence per candidate, so the retry (if any) changes the right knob.

**Answers:** R2

**Blocked by:** none (all inputs exist: both post + raw meshes, sparse models, masks, training logs).

**Status:** in-progress
**Working in:** teammate t06-diagnoser, four audits cheapest-first (2026-10-14); mechanism proposal comes back for lead ruling

- [ ] Cluster audit: re-run the post filter on ONE arm with retained-cluster sweeps (10 → 25 → all); does the sherd region survive as small clusters, or is there nothing coherent to keep? Renders of the sherd box per setting. Decides whether the deleter is the filter or the fusion.
- [ ] Voxel sweep on a sherd crop: re-fuse ONLY the centroid neighbourhood at 0.002 / 0.001 / 0.0005 voxels (crop first — full-scene fine grids will OOM; the spec's tiling note applies); does a surface emerge at any step? Decides grid coarseness, with cost attached.
- [ ] Depth-view audit at the face views (A31_1116/1117): how many views actually constrain the face vs arrive occluded by the clamp? Rendered depth maps + per-view weight contributions at the sherd box. Decides occlusion starvation.
- [ ] Gaussian audit at the sherd: count Gaussians inside the sherd box per arm + their footprint; is the face under-parameterised at training time, before fusion ever runs? Decides whether the failure starts upstream of fusion.
- [ ] Named mechanism with pictured evidence: which of the three (method failed / measurement broken / reference wrong) PLUS the mechanism (e.g. "grid too coarse for a 30 mm occluded face" vs "three of seven face views occluded, TSDF carves conflict") PLUS what would change it and what it costs. No fix built here; no LaMa-vs-control claim made here.

**Rules carried over:** renders before numbers on every candidate; mm provisional until scale provenance exists (unproven A03 factor — do not re-derive, just label); small files to `artifacts/edge_06/`; worker appends work-notes only, never commits, no verdict beyond the named mechanism.
