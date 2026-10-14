# 08: LaMa author baseline — what big-lama proved on, and how our fill compares

**What to build:** the baseline the lead misread in ticket 07 (which searched the PGSR paper; the conservator meant LaMa). We run the authors' code at a pinned commit — so what did the authors show it doing, on what samples, and where are those samples? Then: how does our A31 patch fill read against that reference?

**Answers:** R2

**Blocked by:** none (paper texts, pinned repo + weights, our ticket-02 evidence exist).

**Status:** resolved

## Answer (lead ruling 2026-10-14, work-notes eyed — report ACCEPTED)

Inside/outside call, three axes: (1) MASK SHAPE — inside: our 48px band (1.5% of width) sits below the author narrow max (20px = 3.9% of 512) — the easy side of demonstrated territory. (2) RESOLUTION — outside: ours is 3200 wide; author quant stops at 512, transfer curve at 1536, claim "~2k". We ran 1.6x beyond their claim, 2x beyond their curve. (3) CONTENT — unrepresented: rooms/faces with structure to complete vs our featureless wall with nothing to complete (which is also why our residual reads small — copying plain texture flatters the metric). Plus: the base quant is LaMa-Fourier, NOT big-lama — the weights we run are shown only in figures + a reference curve, with no quantitative cover at any size. Net: our fill result is consistent with the easy corner of the authors' territory, proven at a resolution they never showed, on content they never tested, with weights they never quantified. The ticket-02 "faithful, slightly softer" stands as observed; it carries no author-backed generality. Calibration proposal (Places365 val + author narrow mask + pinned predict.py) is SOUND but uncleared — it downloads external data, so it waits for the conservator.

- [x] Author samples: base quant = LaMa-Fourier (Places 512 + CelebA-HQ 256, narrow/wide/seg); big-lama (51M, Places-Challenge 4.5M) shown in Figs 1/5/6 only. Samples live in figures + dead links only; no runnable sample ships at 786f5936.
- [x] Pinned-code check: ticket-02 driver IS the README path (predict.py + big-lama + default.yaml, CPU hardcoded — matches our run); narrow@512 = strokes ≤20px; no seg-mask config in-repo; eval harness separate from inference path.
- [x] Our-vs-theirs read: mask shape inside (easy side), resolution outside (3200 vs ≤512 quant / 1536 curve / ~2k claim), content unrepresented (plain wall vs rooms/faces); small residual flatters plain texture.
- [x] Baseline proposal: no runnable author sample (dead links); calibration = Places365 val + author narrow mask + pinned predict.py — SOUND, uncleared (external download; conservator decides).
- [x] No LaMa-vs-control verdict; no PGSR claim; quotes filed; smalls in `artifacts/edge_08/`.

**Rules carried over:** worker appends work-notes only, never commits; heavy compute on Spartan only (this ticket should need CPU at most — inference calibration runs only if the baseline proposal is cleared by the lead first, NOT in this ticket).

## Worker work-notes (t08-lamabase, 2026-10-14 — evidence only, no verdicts, no runs)

Paper text fetched with the ticket-07 precedent (`papers/scripts/convert.py 2109.07161 lama`
via the papers venv), moved to `artifacts/edge_08/lama-2109.07161v2.md` so the papers
`check.py` gate stays green (verified `ok: 22 papers`). All paper quotes cite that file
with section/line; all repo refs are raw fetches at pinned commit `786f5936`. Full table:
`artifacts/edge_08/author_test_table.md` (this note is the short form).

(a) Author test table — what big-lama was SHOWN doing:
- Base quant (Table 1, §3, :76-77, :118-122) is LaMa-Fourier, not big-lama: "Places
  ($\bf 512\times 512$)" + "CelebA-HQ ($\bf 256\times 256$)", "LPIPS and FID metrics",
  "for different policies of test masks generation, i.e. narrow, wide, and segmentation
  masks". "For each dataset, we validate the performance across narrow, wide, and
  segmentation-based masks" (:122).
- Big-LaMa (§3.4, :188-192): "18 residual blocks, all based on FFC, resulting in 51M
  parameters", "trained on a subset of 4.5M images from Places-Challenge", "trained only
  on low-resolution $256\times 256$ crops", batch 120, "eight NVidia V100 GPUs for
  approximately 240 hours". Shown in "Figures 1 and 5" (examples) + Figure 6 reference
  curve (:185: "The Big LaMa-Fourier—our best model—is provided for reference").
- Resolution transfer (§3.3, :181-183): "trained using $256\times 256$ crops from
  $512\times 512$ images, on much larger images", "fully-convolutional ... single pass,
  not patch-wise"; FFC models "preserve much more quality and consistency at the
  $1536\!\times\!1536$ resolution". README banner: "~2k" from 256x256 training.
- Training masks (:104-110): "wide masks or box masks strategies" — "polygonal chains
  dilated by a high random width (wide masks) and rectangles of arbitrary aspect ratios
  (box masks)"; test prep "avoid[s] masks which cover more than 50% of an image" (:104).
- Strength/limit (Discussion, :208): "arguably good in generating repetitive visual
  structures (Figure 1, 4)"; "LaMa usually struggles when a strong perspective distortion
  gets involved".
- Where samples live: paper figures only + dead links. Repo tree at 786f5936 has NO image
  folder (root = bin, configs, docker, fetch_data, models, saicinpainting). README:
  "Download test images: unzip LaMa_test_images.zip" (no in-repo source); Links section:
  "Test images from the paper https://disk.yandex.ru/d/xKQJZeVRk5vLlQ" under the banner
  "All yandex dist links went bad". Weights as pinned — README: "The best model (Places2,
  Places Challenge): curl -LJO https://huggingface.co/smartywu/big-lama/resolve/main/big-lama.zip".

(b) Pinned-code / protocol match:
- Ticket-02 driver IS the README path (Inference §§1-3): `python3 bin/predict.py
  model.path=$(pwd)/big-lama indir=$(pwd)/LaMa_test_images outdir=$(pwd)/output`, with
  `configs/prediction/default.yaml` at 786f5936: `dataset: {kind: default, img_suffix:
  .png, pad_out_to_modulo: 8}`, `model.checkpoint: best.ckpt`, `out_key: inpainted`,
  `refine: False`.
- `bin/predict.py` at 786f5936 hardcodes `device = torch.device("cpu")` (default.yaml's
  `device: cuda` not honoured on host path) — matches our CPU run. Mask convention:
  `[name]_maskXXX[suffix]` beside `[name][suffix]`. Output = mask-stem + `.png`, unpadded
  to input size.
- Narrow@512 (`configs/data_gen/random_thin_512.yaml` at 786f5936): irregular strokes,
  `max_width: 20, max_len: 100, min_times: 4, max_times: 70`, `max_tamper_area: 0.5`.
  Wide@512 (`random_thick_512.yaml`): strokes to `max_width: 250, max_len: 450` + boxes
  `bbox_min_size: 30, bbox_max_size: 300, max_times: 4`, `box_proba: 0.3`.
  `configs/data_gen/` holds only thin/medium/thick x 256/512 — no segmentation-mask
  config in-repo. Paper eval harness (30k sampled Places images + FID/LPIPS via
  `fetch_data/places_standard_*` + `bin/evaluate_predicts.py`) is separate from the
  inference path ticket 02 ran.

(c) Our-vs-theirs (numbers, no inside/outside call — lead judges):
- Ours: 48x48 box = 2304 px on 3200x2133 (6,825,600 px) = 0.034% of frame; side 1.5% of
  width. Plain matte wall, gray mean|Δ| 5.51 / rms 6.98 (lead-verified), outside-box 0.
- Author narrow stroke max 20px = 3.9% of 512 width (vs our 1.5%); wide boxes to 300px.
  Author quant ≤512, transfer curve to 1536, claim ~2k — ours 3200 wide. Author content =
  scene-level rooms/faces; ours = featureless wall at ~0.22 mm/px with nothing structural
  to complete.

(d) Calibration proposal (future cleared step, NOT run — read-only ticket):
- Explicit absence: no runnable author sample ships at 786f5936; paper test-image link
  dead per README's own banner.
- Proposal: download Places365-Standard val, sample one 512x512 image, generate author
  narrow mask via pinned `bin/gen_mask_dataset.py` + `random_thin_512.yaml`, run pinned
  `bin/predict.py` + big-lama, score photo residual as ticket 02 did.

(e) Restraint: zero verdicts, zero inference runs, never committed. New files only in
`artifacts/edge_08/` (paper text + table). No PGSR-paper content used (ticket-07
antecedent avoided — this lane is LaMa-only).
