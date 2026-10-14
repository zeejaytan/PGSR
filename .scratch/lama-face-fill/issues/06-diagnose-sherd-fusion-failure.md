# 06: Diagnose why the A31 face fuses to fragments

**What to build:** the mechanism, not a fix. Ticket 04 proved *that* the sherd region fuses to scattered slivers (raw) and a hole (post) in both arms at the stock grid — this ticket finds *why*, with pictured evidence per candidate, so the retry (if any) changes the right knob.

**Answers:** R2

**Blocked by:** none (all inputs exist: both post + raw meshes, sparse models, masks, training logs).

**Status:** resolved

## Answer (lead ruling 2026-10-14, eye on edge_06/ pictures — proposal ACCEPTED)

Method failed via **upstream Gaussian starvation at the small partly-occluded face**. Training deposits effectively no Gaussian cover at the face (generous 3σ: A 35, B 0 of ~650k; nearest 39/65 prov-mm; histogram shows all centres piled ~1 unit out with the box empty territory — eye-confirmed), so TSDF integrates mostly clamp/background depth and yields ≤32-tri confetti that any sane filter deletes. Acquitted with pictures: the keep-10 filter (keep_25 also keeps 0 box verts; biggest coherent box fragment 32 tris vs 173,819 threshold) and the 0.002 grid (nothing deposited for a finer voxel to resolve — sweep correctly not run). Occlusion starvation is OUT (19/28 train views constrain; jaw ≤2% of face). Fix direction, not a claim: face-targeted densification + retrain (~2h45 GPU/arm, no new data) — NOT finer grid, NOT looser filter. Observed asymmetry, unexplained, no verdict: A holds 16 in-box centres (fat) vs B zero. Voxel sweep stays available under the standing sign-off if a future session disagrees with the evidential stop.

- [x] Cluster audit: filter acquitted — keep_25 also keeps 0 box verts; biggest coherent box fragment 32 tris vs 173,819 threshold. Nothing coherent to keep.
- [x] Voxel sweep on a sherd crop: NOT RUN — evidential stop (no deposited signal for a finer voxel to resolve); finer grid would refine noise into finer confetti.
- [x] Depth-view audit: occlusion starvation OUT — 19/28 train views constrain the face, jaw ≤2% of face. (Side note: anchor view A31_1116 is llffhold-test, never fused.)
- [x] Gaussian audit: starvation pictured — 3σ cover A 35 / B 0; nearest 39/65 prov-mm. Failure starts upstream of fusion.
- [x] Named mechanism with pictured evidence: method failed — upstream Gaussian starvation; fix = face-targeted densification + retrain (~2h45 GPU/arm), NOT finer grid / looser filter. No LaMa-vs-control claim.

**Rules carried over:** renders before numbers on every candidate; mm provisional until scale provenance exists (unproven A03 factor — do not re-derive, just label); small files to `artifacts/edge_06/`; worker appends work-notes only, never commits, no verdict beyond the named mechanism.

## Worker work-notes (t06-diagnoser, 2026-10-14)

Job receipts (sacct JobID|JobName|State|ExitCode|Start|End; all sapphire CPU-only):
- 32975387|pgsr-clu06|COMPLETED|0:0|2026-10-14T20:48:17|2026-10-14T20:50:04 (cluster audit, A_lama raw; `slurm/pgsr_diag06_cluster.slurm`)
- 32975388|pgsr-gauss06|COMPLETED|0:0|2026-10-14T20:48:17|2026-10-14T20:48:28 (gaussian audit, both arms; `slurm/pgsr_diag06_gauss.slurm`)
- 32975424|pgsr-dep06|COMPLETED|0:0|2026-10-14T20:49:00|2026-10-14T20:49:09 (depth-view audit; `slurm/pgsr_diag06_depthview.slurm`)
- 32975827|pgsr-cov06|COMPLETED|0:0|2026-10-14T20:55:09|2026-10-14T20:55:17 (gauss coverage follow-up, both arms; `slurm/pgsr_diag06_cover.slurm`)

Staged files (all new, uncommitted; laptop is source of truth, scp'd to Spartan; remote py_compile verified before every submit): `scripts/diag_cluster_06.py`, `scripts/diag_gauss_06.py`, `scripts/diag_depthview_06.py`, `scripts/diag_gausscover_06.py`, `slurm/pgsr_diag06_{cluster,gauss,depthview,cover}.slurm`. Cluster `work/edge_06/{cluster,gauss,depthview,cover}/` (JSONs + PNGs). Laptop `artifacts/edge_06/` (NEW dir): `cluster.json`, `gauss.json`, `depthview.json`, `cover.json`, `cluster_sizes.png`, `keep_all_tri_{0,1}.png`, `A_lama_gauss_{0,1}.png`, `A_lama_footprint.png`, `depthcrop_A31_{1114,1115,1117,1118,1119,1120}.png`, `coverage.png`, `cover_hist.png` — PNGs + KB JSONs only. No LaMa-vs-control claim anywhere below.

Step 0 deviations: (1) first combined multi-dest scp created `scripts/diag_gauss_06.py/` as a directory on Spartan (same stray-dir incident as ticket 04); fixed by rm -rf + individual re-scp, verified by remote py_compile. (2) Harness ssh_list/ssh_exec errored session-wide, so all cluster I/O went over laptop ssh/scp. (3) Depth-view audit ran CPU-only on the extraction-saved JET depth maps + geometric projection — no GPU re-render was needed to answer its question. (4) Voxel sweep NOT run — premise closed by audit 2b (see audit 4 note); no GPU spent.

### Audit 1 — cluster (ONE arm, A_lama raw `tsdf_fusion.ply`, exact `render.py:post_process_mesh` replica)

Method: `cluster_connected_triangles` on the full 10.70M-vert raw mesh once, then threshold = kth-largest cluster (floor 50) for keep=10/25, keep=all = no removal. Box = ticket-04b tight box (centroid [-0.1812, 0.4883, -0.1933], 0.23 units). Box faces = faces with all 3 verts in box. Renders: trisurf box close-ups per setting at the ticket-04 orbits + cluster-size log-log chart.

Pictured: `cluster_sizes.png`, `keep_all_tri_0.png`, `keep_all_tri_1.png` (keep_10/25 have NO renders — their box is empty, nothing to draw; the empty JSON counts are the record).

Flat observations:
- Raw mesh holds 1,005,347 clusters. Top-30 tri counts: 4349171, 1371628, 1226222, 788959, 734134, 295922, 267707, 252712, 209558, 173819, ... (full list in `cluster.json`).
- keep_10: threshold 173,819 tris → 5,128,774 verts / 9,669,832 tris — reproduces the extraction post mesh EXACTLY (ticket-03 mesh_stats) — and 0 verts / 0 faces in the box.
- keep_25: threshold 56,464 tris → 5,879,069 verts / 11,064,711 tris — still 0 verts / 0 faces in the box.
- keep_all (raw): 10,697,082 verts / 14,471,736 tris — box 5,236 verts / 2,390 faces, faces/verts 0.4565.
- The raw box's 2,390 faces fall into HUNDREDS of micro-clusters: largest contributing cluster holds 32 faces (32 tris total, rank 4709); next 18, 10, 10, 9, then 8s and 7s (top-15 in `cluster.json`). The biggest coherent fragment in the box is 32 triangles — ~4 orders of magnitude below the keep_10 threshold.
- Eye on both keep_all trisurfs: diffuse confetti through the box volume, no surface; matches the ticket-04b sliver renders.

### Audit 2 — gaussian (both trained scenes, `point_cloud/iteration_30000/point_cloud.ply`)

Method: manual float32 PLY parse (xyz + sigmoid(opacity) + exp(scale) footprint, mean over axes). Box as above. Renders: scatter of in-box centres per arm at both orbits + footprint histograms (in-box vs global).

Pictured: `A_lama_gauss_0.png`, `A_lama_gauss_1.png`, `A_lama_footprint.png`, `cover_hist.png` (B_ctrl has NO renders — 0 centres in box, nothing to draw).

Flat observations:
- A_lama (673,742 total): 16 centres in box (frac 2.4e-05). B_ctrl (631,016): 0 in box.
- Footprints (scene units): global median A 0.002259 / B 0.002436, p95 A 0.008525 / B 0.008865. A in-box median 0.004521 (~1.69 prov-mm), p95 0.021916 (~8.19 prov-mm) — the few in-box ones are fat.
- Eye on A scatters: 16 lonely points, no structure. Footprint hist: in-box invisible against global.
- Follow-up 2b (3-sigma cover: centre-to-box distance < 3x own footprint): A 35/673742 covering, nearest centre 0.1048 units (~39.2 prov-mm) from centroid; B 1/631016 covering, nearest 0.1729 units (~64.6 prov-mm). Eye on `cover_hist.png`: both arms' centres pile up ~1 unit from the centroid; the box (half-edge 0.115u) is empty territory.

### Audit 3 — depth-view (geometric projection, all 33 views + extraction JET depths)

Method: project the centroid through the shared sparse cameras; per view: front? in-frame? inside the A31 track mask bbox? train or llffhold-test? Cross-checked against `renders_depth/` file presence. Clamp-occlusion px at 1114-1120 CITED from the ticket-03 face_survey jawlike rule (23/276/419/436/404/343/87), not re-derived. Renders: JET depth crops centred on the projected centroid for the 6 TRAIN face views + coverage bar chart.

Pictured: `depthcrop_A31_{1114,1115,1117,1118,1119,1120}.png`, `coverage.png`. Full 33-view table in `depthview.json`.

Flat observations:
- 19 of 28 train views geometrically constrain the face (centroid inside the A31 mask bbox): A31_1101-1107, 1109-1115, 1117-1121. Off-face train views: 1122/1123, 1125-1131 (centroid outside bbox). Test views 1100/1108/1116/1124/1132 never fused (no renders_depth) — including A31_1116, the lead-nominated anchor and the max-occlusion view (436 cited px at 1117, 419 at held-out 1116).
- Face views 1114/1115/1117/1118/1119/1120 are all train, all constrain, all have depth maps; cited jaw occlusion there is 23-436 px (~2% of face at most).
- Eye on the JET crops: smooth far (blue) field with a small near-surface (cyan/green-yellow) blob at the centroid in 1117 (distinct pale blob) and 1114 (yellow-green near patches) — depth maps DO deposit near-geometry at the centroid. JET is per-view normalised, so no metric read; and per audit 2b the cover there is ~nothing, so the blob cannot be read as face (jaw steel sits at the centroid too).

### Audit 4 — voxel sweep on a sherd crop: NOT RUN (premise closed, no GPU spent)

The ticket conditions the sweep on audits 1-3 leaving the grid hypothesis alive. They close it instead: the raw holds no coherent fragment above 32 tris (audit 1), and the trained scenes place effectively no Gaussian cover at the face even at generous 3-sigma (35 in A, 1 in B; nearest 39/65 prov-mm — audit 2b). A finer grid re-fuses the same starved depth field; there is no deposited face signal for a smaller voxel to resolve — it would refine noise into finer confetti. Metric-depth re-render + bounded-volume fusion at 0.002/0.001/0.0005 stays feasible under the standing GPU sign-off should the lead disagree, but nothing in audits 1-3 predicts a surface emerging. No blocking error — an evidential stop, not an infeasible audit.

### PROPOSAL (for the lead's Answer; not a verdict)

- Which of the three: method failed (measurement sound — cameras == COLMAP frame per ticket 04; reference sound — masks eye-passed per ticket 04).
- Mechanism: "upstream Gaussian starvation at a small partly-occluded face" — training places ~zero Gaussian centres within ~40-65 prov-mm of the face (B literally zero, A sixteen fat ones), so TSDF integrates mostly clamp/background depth at the centroid and yields ≤32-tri confetti that any sane cluster filter deletes. The stock 0.002 grid and the keep-10 filter are both acquitted as deleters: keep_25 keeps nothing either, and there is nothing coherent to keep.
- What would change it: face-targeted densification before fusion (seed/clone Gaussians at the face from the 19 constraining views, or relax the pruning that starves small occluded regions) — NOT a finer fusion grid and NOT a looser cluster filter.
- Cost: training-side change + retrain (~2h45 GPU per arm at the observed pace) + re-fuse (~6 min); no new data needed (19 views already constrain).
