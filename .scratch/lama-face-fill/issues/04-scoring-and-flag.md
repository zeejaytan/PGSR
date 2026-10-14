# 04: Scoring — break stability, wall noise, flag-exclusion run

**What to build:** the detail half of R2 plus the honesty mechanism: proof the break did not move, the walls did not roughen, and the generated flag is actually honoured downstream.

**Answers:** R2

**Blocked by:** 03 (training A/B density figures) — extraction + first-look render done 2026-10-14; inputs ready.

**Lead note (read before starting):** 03's auto-crop close-ups missed the sherd (framed fusion-boundary tears at different spots per arm) — crop at the sherd's known 3D location from the photo masks/COLMAP frustums, and attach scale provenance (A03 373.733 mm/unit is assumed, unproven for A31) before any number counts. Gross fusion sanity confirmed; no face verdict stands yet.

**Status:** resolved

## Answer

HONEST NEGATIVE — method failed at the sherd, both arms equally (lead ruling 2026-10-14, eye on edge_04/04b/04c/04d renders): at the approved stock grid (0.002-unit voxels ≈ 0.75 mm), PGSR TSDF fusion yields NO coherent surface for the small partly-occluded A31 face in either arm. Chain: location verified twice (triangulated X in sherd-scale sparse blob; mask bbox encloses projections, track_true and masks agree) → post meshes have a HOLE at X both arms (10-cluster filter kept tray, dropped sherd) → raw meshes hold fragments at the right place (mask-interior verts project as a compact block on the masks) but they are scattered slivers in 3D (faces/verts ~0.47, eye-confirmed in 8 shaded orbits + 4 scatters). Measurement sound (cameras == COLMAP frame, residuals gated), reference sound (masks eye-passed). The three scored checkboxes (break arc, wall noise, flag-exclusion) are REFUSED on this geometry — numbers on fragment soup would be fabrication; the flag run never started for the same reason. The LaMa-vs-control question is unanswerable here through no fault of either arm: no scorable face exists in either. Scale note: A03 373.733 mm/unit stayed provisional throughout — unproven for A31, now moot for scoring. Next-hypothesis (not a claim): finer grid or different surfacing before any LaMa question can be answered on an object this small.
**Lead inspection of 2b-prime overlays (2026-10-14, eye on edge_04c/ side-by-sides):** plume overlaps the mask bbox with centroid inside in all 4 panels — track_true and masks agree, location stands (the brown triangle is a neighbouring sherd; A31's face is the occluded region behind the clamp in these views). NOT decisive: the 86 mm box swallows clamp + background, so "right neighbourhood" is proven but "face present/absent" is not. 2b-prime-2 ordered: shade + project ONLY mask-interior verts (~60%, ~3.2k/arm); coherent patch on the face region = scorable, still-slivers = name method-failed with this evidence.

**Lead inspection of phase 2a (2026-10-14, eye on edge_04b/ shaded close-ups):** both arms show scattered slivers, no continuous face (faces/verts ~0.46: A 5235/2390, B 4442/2093 in the tight box) — worker's flat read eye-confirmed. 2b scoring NOT cleared: relief/arc numbers on fragment soup would be meaningless. Phase 2b-prime ordered instead: project raw-box verts through face-visible training cameras (e.g. A31_1116/1117) onto the photos, to decide whether the surface is genuinely absent (method failed) or badly viewed (measurement broken). Note for the record: the 0.75 mm fusion grid is ~4x coarser than the 0.2 mm ridge scale, so the ridge question is out of this grid's reach regardless.

**Lead inspection of phase 1 (2026-10-14, eye on edge_04/ renders):** location ACCEPTED (X sits in a sherd-scale sparse blob, both arms). Post meshes UNSCORABLE at the sherd — eye-confirmed hole at X in both arms (white void in see_xz, larger in B): the 10-cluster filter kept tray background and dropped the sherd region in both arms. Raw meshes hold the sherd (21k/30k verts in box) but phase-1 scatters are unshaded clouds — no coherent face confirmable by eye yet. Curtain streaks are shared input-side structure (present in sparse too), not an arm difference. Consequence: ALL scoring moves to RAW meshes; phase 2a must deliver shaded-surface close-ups at tighter framing before any number is read.

- [ ] Break-face arc agreement A−B in mm of arc on 2–3 sampled edges, far below erosion width; any break move recorded as contamination
- [ ] Flat-wall noise A vs B as RMS residual in mm on quiet faces
- [ ] Generated-vs-measured flag written in the PLY and proven honoured by a matcher run that demonstrably excludes flagged vertices (colour alone does not count)
- [ ] Scale provenance attached (unscaled results refused, not measured); which of the three the outcome is named (method failed / measurement broken / reference wrong)

## Worker work-notes (t04-scorer, 2026-10-14)

Job receipts (sacct JobID|JobName|State|ExitCode|Start|End, all sapphire, CPU-only):
- 32948403|pgsr-render-edge-04|COMPLETED|0:0|2026-10-14T14:52:20|2026-10-14T14:53:00 (locate+render, post meshes; new `slurm/pgsr_render_edge_04.slurm`)
- 32948631|pgsr-diag04|COMPLETED|0:0|2026-10-14T15:00:14|2026-10-14T15:00:34 (frame diagnosis, --wrap)
- 32948817|pgsr-void04|COMPLETED|0:0|2026-10-14T15:02:46|2026-10-14T15:02:58 (void probe, --wrap)
- 32948969|pgsr-see04|COMPLETED|0:0|2026-10-14T15:07:56|2026-10-14T15:08:16 (side-view renders, --wrap)
- 32949131|pgsr-raw04|COMPLETED|0:0|2026-10-14T15:11:41|2026-10-14T15:11:54 (raw-mesh box counts, --wrap)
- 32949285|pgsr-rawrender04|COMPLETED|0:0|2026-10-14T15:15:05|2026-10-14T15:15:22 (locate+render, raw meshes, --wrap)
- 32949602|pgsr-slab04|COMPLETED|0:0|2026-10-14T15:20:52|2026-10-14T15:21:07 (slab test, --wrap)
- 32949894|pgsr-scat04|COMPLETED|0:0|2026-10-14T15:24:50|2026-10-14T15:25:05 (locate+render raw as scatter, --wrap)

Step 1 deviation (no pull, nothing forced): Spartan repo is `HEAD (no branch)` detached with staged entries, which is the documented normal trial state (PGSR AGENTS.md: pull would move HEAD). `git pull --ff-only` is not applicable there, so no pull was attempted and nothing was moved. Laptop repo was clean (`main...origin/main`).

Location method (one method, both arms): back-project A31-component bbox centres (mask-derived, `lama_trial/ticket03/face_survey/track_true.json`, native 5568x3712 divided by 1.74 to the 3200x2133 sparse frame) from the 7 face-visible views A31_1114-1120 through the shared 33-camera sparse model (PINHOLE 3200x2133, fx=6829.81/fy=6829.36/cx=1600/cy=1066.5), least-squares ray intersection. `images.bin` md5 is identical for both arms, so one triangulation serves both.

Centroid (both arms, same numbers): scene units [-0.1812, 0.4883, -0.1933]; provisional mm [-67.7, 182.5, -72.2] (A03 373.733 scale, unproven for A31). Reprojection residuals px (s3200) [17.5, 8.9, 9.2, 17.8, 13.0, 10.0, 47.6], mean 17.7 (gate was 25; view 1120 is the largest at 47.6). Face width from triangulated depth ~0.109 units (~41 mm provisional); box = 0.400 units (~149 mm provisional, clamped floor of the 2.5x rule).

Box size: 0.400 scene units (~149 mm provisional), same centroid/box/viewpoints for every render. Close-up viewpoints el=30/az=-60 and el=10/az=30; 50 mm provisional scale bar drawn on close-ups.

Staged files (all new, uncommitted; laptop is source of truth, scp'd to Spartan): `scripts/locate_a31_render_04.py` (triangulate + render; later args: optional mesh filename; close-ups switched from shaded triangles to z-coloured scatter after the raw mesh proved too fragmented for shaded rendering), `scripts/diag_frame_04.py`, `scripts/diag_void_04.py`, `scripts/diag_see_04.py`, `scripts/diag_raw_04.py`, `scripts/diag_slab_04.py`, `slurm/pgsr_render_edge_04.slurm`. Cluster `work/edge_04/` (post-mesh renders + locate.json + diag side views) and `work/edge_04_raw/` (raw-mesh renders + locate.json; its diag/ subdir was removed by the scatter rerun — laptop copies kept). Laptop `artifacts/edge_04/`: `locate.json`, `A_lama/{closeup_0,closeup_1,context,see_xz,see_yz}.png`, `B_ctrl/{...same...}.png`, `raw/{locate.json, A_lama/{closeup_0,closeup_1,context,slab_xz}.png, B_ctrl/{...same...}.png}` — PNGs + KB JSON only. (Stray-dir incident: the first combined scp created `scripts/locate_a31_render_04.py/` as a directory on Spartan; fixed by moving the file up and removing the dir, verified by remote py_compile. Harness ssh_list/ssh_exec errored session-wide, so all cluster I/O went over laptop ssh/scp.)

Flat observations (descriptive only):
- Post meshes (`tsdf_fusion_post.ply`): 0 verts / 0 faces in the 0.4-unit box around the centroid in BOTH arms (5.13M / 5.88M verts total). Post close-ups show empty axes; context views show the red crop box inside the dense footprint.
- Side-view scatters (post mesh blue, sparse red, X green star): the mesh forms a shell around a central void; the dense red sparse cluster (6640 sparse points within 0.2 units of X) and the star sit inside that void in both arms.
- Frame check: train `cameras.json` position for A31_1100 equals the COLMAP centre to 4 decimals ([0.1911, -2.5298, -2.901]); the loader applies no world normalisation, so the mesh frame is the COLMAP frame.
- Raw meshes (`tsdf_fusion.ply`): box holds A_lama 21,194 verts / 9,962 faces, B_ctrl 30,041 verts / 14,568 faces (raw totals 10.70M / 11.03M verts). The sherd region was fused, then removed by the post small-component filter.
- Slab test (raw box content): z spans the full box floor to ceiling both arms (10-90% thickness ~115-118 mm provisional of the 149 mm box); x-z view shows three vertical curtain-like bands, the middle one centred near X.
- Raw scatter close-ups (both viewpoints, both arms): a diffuse point cloud roughly filling the box; no clean face surface is resolvable by eye in these views. Raw faces/verts ratio ~0.5 (fragmented).

## Worker work-notes (t04-scorer, phase 2a, 2026-10-14)

Task: shaded-surface (trisurf) close-ups of a tighter box on RAW meshes only. No scoring, stopped after staging.

Job receipts (sapphire, CPU-only):
- 32950874|pgsr-tight04b|FAILED|1:0|2026-10-14T15:33:08|2026-10-14T15:33:15 — submitted with a broken script (a local edit had collapsed `def qvec_to_R(q):` and its body onto one line; IndentationError before any output). No files written by the job.
- 32950981|pgsr-tight04b|COMPLETED|0:0|2026-10-14T15:35:00|2026-10-14T15:35:16 — rerun after fix (remote py_compile verified before resubmit), `--wrap` calling `scripts/locate_a31_render_04.py work/edge_04b tsdf_fusion.ply auto trisurf`.

Script change (same file, still uncommitted): new optional args `[box|auto] [style]`; `auto` derives the box from the sparse blob extent (p5-p95 spread per axis of sparse points within 0.3 units of X, x1.2 cover, ceil to 0.01, clamped to [0.10, 0.25]); `style` selects trisurf (default, restored) vs scatter. Scale bar auto: 20 mm provisional when the box is under 100 mm provisional, else 50 mm.

Box (same both arms, from the shared sparse): blob near X n=6646, p5=[-0.217, 0.386, -0.285], p95=[-0.149, 0.576, -0.113], spread=[0.069, 0.190, 0.172] → box=0.230 units (~86 mm provisional). Centroid unchanged from phase 1. Tight-box contents: A_lama 5,235 verts / 2,390 faces; B_ctrl 4,442 verts / 2,093 faces.

Staged files: cluster `work/edge_04b/` (`locate.json` + `A_lama/` + `B_ctrl/`, closeup_0/1 + context each). Laptop `artifacts/edge_04b/` (NEW dir; `edge_04/` untouched): `locate.json`, `A_lama/{closeup_0,closeup_1,context}.png`, `B_ctrl/{closeup_0,closeup_1,context}.png` — PNGs + KB JSON only. `scripts/locate_a31_render_04.py` updated on both sides (laptop source of truth, scp'd, remote py_compile OK).

Flat observations (descriptive only):
- Both close-up viewpoints in both arms render as scattered shaded slivers, not a continuous surface; faces/verts ratio ~0.46 in the tight box.
- A_lama el=30/az=-60: fragments spread through the whole 86 mm box with a denser patch near the top-centre; el=10/az=30: fragments spread through the box, slightly denser toward the left half.
- B_ctrl el=30/az=-60: fragments spread through the box with a denser vertical streak near the top-centre; el=10/az=30: fragments spread through the box with a denser patch toward the upper right.
- Context views: the red 86 mm crop box sits at the same footprint position as the phase-1 box centre in both arms.
- No clean face surface is resolvable by eye in any of the four shaded close-ups.

## Worker work-notes (t04-scorer, phase 2b-prime, 2026-10-14)

Task: diagnostic projection of raw-box verts through 2 training views' COLMAP cameras onto the photos, then STOP. No scoring done.

Job receipts (sapphire, CPU-only):
- 32951970|pgsr-proj04c|FAILED|1:0|2026-10-14T15:46:36|2026-10-14T15:46:46 — new script's images.bin reader treated the image name as length-prefixed; COLMAP stores it null-terminated, so the parse ran off-rails (MemoryError). My transcription error copying the reader; the working null-terminated version sits in `scripts/locate_a31_render_04.py` lines 60-78.
- 32952360|pgsr-proj04c|COMPLETED|0:0|2026-10-14T15:50:57|2026-10-14T15:51:16 — rerun after replacing the reader with the exact working version (remote py_compile passed before submit).

Script (new, uncommitted): `scripts/diag_project_04.py` (laptop source of truth, scp'd to Spartan). Reads centroid+box from `work/edge_04b/locate.json` (note: centroid re-read at the JSON's 4-decimal rounding, so box membership differs by 1 vert per arm from phase 2a: A 5236 vs 5235, B 4443 vs 4442; fractions unaffected at 3 decimals). Shared 33-camera sparse model, per-arm own photo dir (the two arms' JPGs are byte-different: LaMa-inpainted vs control). Views A31_1116.JPG + A31_1117.JPG. Overlays at 0.4 scale (1280x853 panels): cyan = projected in-photo box verts, red = track mask bbox (/1.74 into the 3200-frame), yellow cross = projected centroid.

Staged files: cluster `work/edge_04c/` (`project.json` + 4 per-arm overlays + 2 side-by-sides). Laptop `artifacts/edge_04c/` (NEW dir; `edge_04/` + `edge_04b/` untouched): `project.json`, `A_lama/B_ctrl x 1116/1117 _overlay.png`, `sidebyside_A31_1116/1117.png` — PNGs + KB JSON only.

Fractions (from `project.json`):
- A31_1116: A_lama 5236 verts, 1.000 in photo, 0.607 in mask; B_ctrl 4443 verts, 1.000 in photo, 0.616 in mask.
- A31_1117: A_lama 5236 verts, 1.000 in photo, 0.609 in mask; B_ctrl 4443 verts, 1.000 in photo, 0.600 in mask.

Flat observations (descriptive only):
- All four panels show the same rig: a horizontal bar of clamps, with the brown triangular sherd fragment held in a clamp left-of-centre.
- The cyan projected verts form a tall vertical plume that sits over the clamp hardware and the dark background above/behind it; the brown sherd lies to the left of the plume's centre in all four panels.
- The red mask bbox encloses the middle of the plume; the yellow centroid cross sits inside the plume, above the clamp jaws.
- The plume extends from the clamp level up into empty background; in the B_ctrl panels a second smaller cyan streak sits to the right of the main plume.
- 100% of box verts land inside the photo frame in both views and both arms; ~60-62% land inside the mask bbox.

## Worker work-notes (t04-scorer, phase 2b-prime-2, 2026-10-14)

Task: mask-interior box verts only — shaded trisurf free-orbit (same 2 viewpoints) plus their photo projection, per arm x both views, then STOP. No scoring done.

Job receipt (sapphire, CPU-only):
- 32953297|pgsr-mpatch04d|COMPLETED|0:0|2026-10-14T15:58:27|2026-10-14T15:58:47 — first submit, no rerun. `--wrap` calling new `scripts/diag_maskpatch_04.py work/edge_04d` (readers copied exactly from the verified locate script; remote py_compile passed before submit).

Script (new, uncommitted): `scripts/diag_maskpatch_04.py` (laptop source of truth, scp'd to Spartan). Same centroid+box as 2b-prime (rounded JSON values). Per arm x view: box verts projected through the shared sparse camera; kept = inside the track mask bbox; submesh = faces with all 3 verts kept; shaded trisurf at el=30/az=-60 and el=10/az=30 with 20 mm provisional bar; photo overlay of kept verts only at 0.4 scale with red mask bbox.

Exact mask-interior counts (from `maskpatch.json`, identical to 2b-prime fractions):
- A31_1116: A_lama 3180/5236 verts kept, 1498 faces; B_ctrl 2736/4443 verts kept, 1311 faces.
- A31_1117: A_lama 3187/5236 verts kept, 1503 faces; B_ctrl 2664/4443 verts kept, 1279 faces.

Staged files: cluster `work/edge_04d/` (`maskpatch.json` + 12 PNGs). Laptop `artifacts/edge_04d/` (NEW dir; earlier dirs untouched): `maskpatch.json`, per arm x view `{tri_0, tri_1, maskproj}.png` — PNGs + KB JSON only.

Flat observations (descriptive only):
- Maskproj overlays: the kept verts project as a compact cyan block that fills the red mask bbox in all four panels; the block sits over the clamp jaws and the dark region directly above them, with the brown triangular sherd to its left.
- Trisurf free-orbits (all 8): the kept verts render as scattered shaded slivers spread through the cropped volume; faces/verts ratio ~0.47 in every panel (1498/3180, 1311/2736, 1503/3187, 1279/2664). No continuous patch surface is resolvable by eye in any of the eight views.
- A_lama panels read as a diffuse spread through the volume; B_ctrl panels show a denser vertical streak near the top in the el=30/az=-60 viewpoint.
