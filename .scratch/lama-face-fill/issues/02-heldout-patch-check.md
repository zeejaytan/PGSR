# 02: Inpaint held-out face patch and check it tracks known skin

**What to build:** the stop-or-go gate for the whole trial: a known face patch held out, filled by the pinned LaMa build, and compared to its true surface — so that clamp holes are only touched by a fill already shown to track real skin.

**Answers:** R2

**Blocked by:** 01 (pin record).

**Status:** ready-for-agent

- [ ] Held-out known face patch filled at full photo resolution; deviation from true surface reported in mm
- [ ] Patch deviation within the face tolerance stated in R2; if it misses, the trial stops here and R2 records the miss with a date
- [ ] Patch close-up renders staged at a view resolving fine face texture, before any clamp pixel is touched
- [ ] Jaw-contact region confirmed excluded from fill and from damage-scoring
