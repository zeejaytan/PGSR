# 07: Why does the face starve — and what did the authors test on?

**What to build:** the reason behind ticket 06's cause, plus an external baseline. Ticket 06 proved *that* training deposits no Gaussians at the face; it did not say *why* densification avoids it, nor whether the authors' own results cover anything like our case. This ticket answers both or reports honestly that it cannot.

**Answers:** R2

**Blocked by:** none (paper texts + pinned repo + our logs exist).

**Status:** in-progress
**Working in:** teammate t07b-baseliner, paper baseline + densification audit (2026-10-14 retry; t07-baseliner died unresponsive with no report — rebuild reuses any verified leavings first)

- [ ] Author baseline: via the `paper-reader` helper (`.claude/agents/`, plain texts in `C:\PR\papers\`), list what scenes/datasets the PGSR paper tests surface reconstruction on (with quotes + file/section, never a verdict from memory): scene scales, object sizes, any small/occluded/thin objects. Is there anything sherd-scale in their results?
- [ ] Pinned-code densification audit: in the PGSR version we run, identify the densification/pruning parameters and rules (gradient thresholds, opacity resets, clone/split conditions) that decide where Gaussians grow and die. Quote file + line.
- [ ] Reason hypothesis with evidence: given the above, why would a small, plain-walled, partly clamp-held face get ~zero cover while 19 views see it? (Candidates: low image gradients on plain wall → no densify signal; pruning kills small occluded-region Gaussians; SfM seed sparse there.) Test at least one cheaply — e.g. compare image-gradient energy inside the face mask vs a well-built wall region, or count SfM seed points at the face vs elsewhere.
- [ ] Baseline proposal: the closest author-tested case to ours, stated as the reference point our result should be read against — or "no comparable author case exists," which itself is a finding (domain gap, not a defect).
- [ ] No fix built here; no LaMa-vs-control claim; renders before numbers where a picture is load-bearing.

**Rules carried over:** worker appends work-notes only, never commits; small files to `artifacts/edge_07/`; paper claims carry quotes with file + section.
