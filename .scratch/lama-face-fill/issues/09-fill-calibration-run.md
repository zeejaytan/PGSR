# 09: Fill calibration run — our pinned LaMa on an author-style case

**What to build:** the cleared calibration from ticket 08: one Places365-Standard val image + author narrow mask through our pinned fill, scored as ticket 02, set beside our A31 patch numbers.

**Answers:** R2

**Blocked by:** none (conservator cleared 2026-10-14).

**Status:** resolved

## Answer (lead ruling 2026-10-14, side-by-side eyed — calibration BEHAVES AS THE AUTHORS' DOES)

Our pinned setup completes structured content properly: beams, railing, sofas, bottle and glasses continue across a ~30% author-narrow mask with no visible breaks, slightly soft 1:1 — eye-confirmed. Numbers: gray mean|Δ| 8.60 / rms 16.50 (N=78,597) beside ticket-02's 5.51 / 6.98 (N=2,304 plain wall) — same order of magnitude, higher on much harder content, as expected. Caveats (weight = one image): mask fraction differs wildly (30% vs 0.034%), so this is a lead-grade check, not a proof; and it retires the worry that our 3200px ticket-02 run was off-distribution-broken — the same setup does the job at author size. Ticket 02's "faithful, slightly softer" keeps its observed standing, now with a worked calibration behind it.

- [x] Fetch ONE Places365-Standard val image (512x512; record source URL + checksum); generate the author narrow mask with the pinned `bin/gen_mask_dataset.py` + `configs/data_gen/random_thin_512.yaml` at commit `786f5936`.
- [x] Run the pinned `bin/predict.py` + big-lama weights (CPU path, as ticket 02) on that image + mask.
- [x] Score the fill with `PGSR/scripts/measure_patch_deviation.py` (ticket-02 instrument) and set beside ticket 02's A31 numbers (gray mean|Δ| 5.51 / rms 6.98): does our setup reproduce author-territory behaviour on author content?
- [x] Verdict reserved to the lead: report numbers + renders, no generality claim. Small files to `artifacts/edge_09/`.

**Rules carried over:** worker appends work-notes only, never commits; heavy compute on Spartan only (CPU expected); no LaMa-vs-control claim.

## Worker work-notes (t09-calibrator, 2026-10-14 — evidence only, no verdicts)

(a) Image + mask provenance: one Places365-Standard val image, `val_256/Places365_val_00035900.jpg`
(first image member of `https://data.csail.mit.edu/places/places365/val_256.tar`, live, 525,158,400 bytes;
saved 256x256 RGB, sha256 `e6ca786c…2bc3`). Mask via pinned `bin/gen_mask_dataset.py` +
`random_thin_512.yaml` @`786f5936` (unseeded np.random; 512x512 upscale+crop, 78,597 px = 29.98%).
Dead ends: `places2.../val_large.tar` + `test_large.tar` both 404; download.html now form-gated.

(b) Run receipts: job 32983094 (genmask+predict, CPU) COMPLETED 0:0 00:00:38, node spartan-bm015,
1/1 in 4.23s; job 32983291 (score) COMPLETED 0:0 00:00:01. Commit `786f5936` + predict.py CPU line 44
verified in-job; big-lama weights as pinned; outside-mask max|Δ| = 0.0.

(c) Scored numbers (ticket-02 gray method, mask pixels; no mm_proxy): mean|Δ| 8.60 / rms 16.50 /
p50 4.33 / p90 19.33 / max 187.0 / bias −1.57 (N=78,597). Beside ticket-02 A31: 5.51 / 6.98
(N=2,304, 48px plain-wall box). Renders + stats.json + provenance.txt in `artifacts/edge_09/`;
Spartan work area `lama_trial/edge09/`. Note: `measure_patch_deviation.py` hardcodes the A31
gate02 layout, so scoring used a script replicating its gray formulas over mask pixels
(`lama_trial/edge09/score_edge09.py`); mm_proxy omitted (no depth scale on a Places photo).

(d) Flat observations: content is a structured hotel-lobby interior (beamed vault ceiling, sofas,
table with bottle/glasses/candle) — not plain wall. At preview scale the fill continues beams,
sofa edges and bottle/glass shapes without visible breaks; 1:1 fill reads slightly softer than
true in stroked areas. Mask covers ~30% of frame (near the yaml 0.5 tamper cap). Zero verdicts.
