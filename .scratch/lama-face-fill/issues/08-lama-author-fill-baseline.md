# 08: LaMa author baseline — what big-lama proved on, and how our fill compares

**What to build:** the baseline the lead misread in ticket 07 (which searched the PGSR paper; the conservator meant LaMa). We run the authors' code at a pinned commit — so what did the authors show it doing, on what samples, and where are those samples? Then: how does our A31 patch fill read against that reference?

**Answers:** R2

**Blocked by:** none (paper texts, pinned repo + weights, our ticket-02 evidence exist).

**Status:** in-progress
**Working in:** teammate t08-lamabase, LaMa paper + repo baseline (2026-10-14); calibration proposal returns for lead ruling (no runs in this ticket)

- [ ] Author samples: via the `paper-reader` helper (plain texts in `C:\PR\papers\`, quotes with file + section), what does the LaMa paper test big-lama inpainting on (datasets, mask types — narrow/wide/box/segmentation, resolutions)? Where do those test samples live (paper figures only, downloadable set, repo demo images)? The question is what the authors *showed*, not what the model can do in principle.
- [ ] Pinned-code check: at our pinned LaMa commit (`786f5936`, per R2 pin), do the repo's own demo/test images + default inference settings match the paper's protocol? Quote README/paths.
- [ ] Our-vs-theirs read: ticket 02's A31 patch result (48px face-only patch, gray mean|Δ| 5.51 / rms 6.98, evidence `artifacts/lama02_eye/`) set beside the closest author case — mask size in px, texture class (plain wall vs the authors' scenes), and viewing conditions. Is our use (narrow-band mask on plain pot wall at 3200px) inside or outside what the authors demonstrated?
- [ ] Baseline proposal: the concrete author sample + mask we should run our pinned fill on as a calibration (same code, same weights, their image), so "our fill behaves as the authors' does" becomes a checkable claim — or "no runnable author sample exists," stated explicitly.
- [ ] No LaMa-vs-control verdict; no PGSR claim; paper quotes carry file + section; small files to `artifacts/edge_08/`.

**Rules carried over:** worker appends work-notes only, never commits; heavy compute on Spartan only (this ticket should need CPU at most — inference calibration runs only if the baseline proposal is cleared by the lead first, NOT in this ticket).
