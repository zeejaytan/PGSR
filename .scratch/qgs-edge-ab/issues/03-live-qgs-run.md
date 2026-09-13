# 03: Live QGS train-plus-extract, one capture one seed

**What to build:** one pinned QGS training at full capture density plus one extraction at the same voxel with the stated masks — the only GPU the trial is allowed before scoring.

**Answers:** R1

**Blocked by:** 01 pin QGS source (GO required — missing mask construction stops here), 02 PGSR-A baseline (control must exist first).

**Status:** ready-for-agent

- [ ] Single QGS training on `A03_sherds` at full resolution (no silent downsample), one seed, run values as pinned in 01; held-out views kept honest where the build supports them
- [ ] Single extraction at the stated voxel/band in mm with the stated mask construction; block counts and free-memory figures printed before the call; training-time masking and post-training pruning untouched per M4/M5
- [ ] Outputs archived without overwriting each other; mesh stats (verts, pieces, bounds vs training points) printed; no batch submission without explicit approval, laptop-side poll on the submit
- [ ] A block/OOM-class crash is recorded as the known ceiling (R1 becomes the tiling question by amendment), not a new mystery and not a silent workaround
