# 09: Fill calibration run — our pinned LaMa on an author-style case

**What to build:** the cleared calibration from ticket 08: one Places365-Standard val image + author narrow mask through our pinned fill, scored as ticket 02, set beside our A31 patch numbers.

**Answers:** R2

**Blocked by:** none (conservator cleared 2026-10-14).

**Status:** in-progress
**Working in:** teammate t09-calibrator, one-image calibration run (2026-10-14, conservator-cleared); numbers return for lead ruling

- [ ] Fetch ONE Places365-Standard val image (512x512; record source URL + checksum); generate the author narrow mask with the pinned `bin/gen_mask_dataset.py` + `configs/data_gen/random_thin_512.yaml` at commit `786f5936`.
- [ ] Run the pinned `bin/predict.py` + big-lama weights (CPU path, as ticket 02) on that image + mask.
- [ ] Score the fill with `PGSR/scripts/measure_patch_deviation.py` (ticket-02 instrument) and set beside ticket 02's A31 numbers (gray mean|Δ| 5.51 / rms 6.98): does our setup reproduce author-territory behaviour on author content?
- [ ] Verdict reserved to the lead: report numbers + renders, no generality claim. Small files to `artifacts/edge_09/`.

**Rules carried over:** worker appends work-notes only, never commits; heavy compute on Spartan only (CPU expected); no LaMa-vs-control claim.
