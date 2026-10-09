# 01: Pin LaMa build, mask construction, and measurement record

**What to build:** the repeatable source record the whole trial stands on: LaMa commit + weights named, inpaint mask construction stated, extraction voxel/band in mm stated, control inputs named — so that every later ticket runs something pinned, not something that drifts.

**Answers:** R2

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] LaMa commit hash + weights recorded in R2 before anything runs
- [ ] Mask construction stated: which pixels (clamp/rig only), dilation px, cross-view propagation; break pixels and jaw-contact region explicitly excluded
- [ ] Extraction voxel size and truncation band stated in mm for both arms; control input dataset named with view count and resolution
- [ ] One sherd chosen and named; identical seed/config/iterations recorded for both arms
- [ ] Env reuse-first: existing Spartan env named with the additive delta (if any) stated; fresh env only on a failed import probe
