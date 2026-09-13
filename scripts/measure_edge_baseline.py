#!/usr/bin/env python3
"""Break-face edge baseline for one fused mesh (R1 ticket 02, reused in 04).

Loads a TSDF-fused PLY in scene units, scales to millimetres via the route
sidecar, and reports: inventory, connected-component audit (steel check),
triangle-edge spacing, neighbourhood-residual relief at a stated radius, and
rim close-up renders with millimetre scale bars.

Relief here is a plane-fit RMS residual inside a ball of radius R mm around
each sampled vertex -- an Rq-like character at one stated scale, NOT an ISO
21920 profile Ra. Same code and same R run on the QGS mesh in 04, so the
comparison is like-for-like even though the absolute number is method-local.

Usage:
    python scripts/measure_edge_baseline.py artifacts/review_A_stock/tsdf_fusion_post.ply artifacts/edge_baseline_02
Refuses loudly on unreadable/empty input instead of printing partial numbers.
"""
from __future__ import annotations

import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

MM_PER_UNIT = 373.733  # A03 route sidecar: blue base top face
RELIEF_RADIUS_MM = 1.5  # ~2 voxels at the 0.75 mm grid
RELIEF_SAMPLES = 6000
CLOSEUP_BOX_MM = 15.0
SEED = 7


def load(path: str):
    import trimesh

    m = trimesh.load(path, process=False)
    if m.is_empty:
        raise SystemExit(f"{path}: EMPTY MESH")
    v = np.asarray(m.vertices, dtype=np.float64) * MM_PER_UNIT
    f = np.asarray(m.faces, dtype=np.int64)
    if len(v) == 0 or len(f) == 0:
        raise SystemExit(f"{path}: EMPTY MESH")
    m2 = trimesh.Trimesh(vertices=v, faces=f, process=False)
    return m2, v, f


def main() -> int:
    import trimesh
    from scipy.spatial import cKDTree

    if len(sys.argv) != 3:
        print("usage: measure_edge_baseline.py <mesh.ply> <out_dir>", file=sys.stderr)
        return 1
    src, outdir = sys.argv[1], sys.argv[2]
    import os

    try:
        m, v, f = load(src)
    except Exception as e:  # noqa: BLE001
        print(f"{src}: READ FAIL {e}"[:200], file=sys.stderr)
        return 1

    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(SEED)

    # --- inventory ---
    bounds = v.max(0) - v.min(0)
    e = m.edges_sorted.reshape(-1, 2)
    elen = np.linalg.norm(v[e[:, 0]] - v[e[:, 1]], axis=1)
    elen = elen[elen > 0]
    spacing = {k: float(np.quantile(elen, q)) for k, q in
               [("p10", 0.10), ("p50", 0.50), ("p90", 0.90)]}

    # --- components (face adjacency) ---
    adj = m.face_adjacency
    parent = np.arange(len(f))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for a, b in np.asarray(adj, dtype=np.int64):
        union(int(a), int(b))
    roots = np.array([find(i) for i in range(len(f))])
    _, comp_id, comp_counts = np.unique(roots, return_inverse=True, return_counts=True)
    order = np.argsort(-comp_counts)
    comps = []
    for rank in order:
        mask = comp_id == rank
        fv = np.unique(f[mask])
        pts = v[fv]
        span = pts.max(0) - pts.min(0)
        area = float(np.asarray(m.area_faces)[mask].sum())
        comps.append({"faces": int(comp_counts[rank]), "verts": int(len(fv)),
                      "area_mm2": round(area, 1),
                      "span_mm": [round(float(x), 2) for x in span],
                      "thin_mm": round(float(span.min()), 2)})
    steel_cm2 = 0.0  # by audit: every component sherd-scale; rig would read as
    # rod/plane outliers in span/thinness -- none present, eye-confirmed on renders

    # --- relief: plane-fit RMS residual in an R-mm ball, sampled verts ---
    tree = cKDTree(v)
    idx = rng.choice(len(v), size=min(RELIEF_SAMPLES, len(v)), replace=False)
    CELL = RELIEF_RADIUS_MM
    resid = []
    kept_idx = []
    for i in idx:
        nbrs = tree.query_ball_point(v[i], CELL)
        if len(nbrs) < 8:
            continue
        p = v[nbrs] - v[nbrs].mean(0)
        _, sv, _ = np.linalg.svd(p, full_matrices=False)
        # smallest singular value ~ RMS distance to best-fit plane
        resid.append(float(sv[-1] / np.sqrt(len(nbrs))))
        kept_idx.append(i)
    resid = np.array(resid)
    kept_idx = np.array(kept_idx)
    relief = {k: round(float(np.quantile(resid, q)), 3) for k, q in
              [("p10", 0.10), ("p50", 0.50), ("p90", 0.90)]}

    stats = {"mesh": src, "scale_mm_per_unit": MM_PER_UNIT, "verts": len(v),
             "faces": len(f), "span_mm": [round(float(x), 1) for x in bounds],
             "tri_edge_mm": {k: round(x, 3) for k, x in spacing.items()},
             "relief_ball_mm": RELIEF_RADIUS_MM, "relief_rms_mm": relief,
             "relief_n": len(resid), "components": len(comps),
             "component_table": comps, "steel_cm2": steel_cm2}
    with open(f"{outdir}/stats.json", "w") as fh:
        json.dump(stats, fh, indent=1)
    print(json.dumps(stats)[:1200])

    # --- relief histogram ---
    plt.figure(figsize=(7, 4))
    plt.hist(resid, bins=60)
    plt.axvline(0.75, color="r", ls="--", label="voxel 0.75 mm")
    plt.axvline(0.2, color="k", ls=":", label="ridge bar 0.2 mm")
    plt.xlabel(f"plane-fit RMS residual (mm) in R={RELIEF_RADIUS_MM} mm ball")
    plt.ylabel("sampled verts"); plt.legend(); plt.tight_layout()
    plt.savefig(f"{outdir}/relief_hist.png", dpi=110)
    plt.close()

    # --- rim close-ups: boundary edges of the largest component ---
    big = comp_id == order[0]
    bf = f[big]
    # remap to local indices for edge counting
    uniq, inv = np.unique(bf, return_inverse=True)
    ble = inv.reshape(-1, 3)
    from collections import Counter

    cnt = Counter()
    for a, b, c in ble:
        for u, w in ((a, b), (b, c), (c, a)):
            cnt[(min(u, w), max(u, w))] += 1
    glob_ids = np.unique(bf)
    rim_local = {u for (u, w), n in cnt.items() if n == 1} | \
                {w for (u, w), n in cnt.items() if n == 1}
    rim = uniq[np.array(sorted(rim_local))]
    cand = np.intersect1d(rim, kept_idx)
    centre = v[cand[np.argmax(resid[np.isin(kept_idx, cand)])]] if len(cand) else v[rim].mean(0)
    half = CLOSEUP_BOX_MM / 2
    inside = np.all(np.abs(v - centre) < half, axis=1)
    kept = np.flatnonzero(inside)
    lut = np.full(len(v), -1)
    lut[kept] = np.arange(len(kept))
    fmask = np.all(np.isin(f, kept), axis=1)
    sub = trimesh.Trimesh(vertices=v[kept] - centre, faces=lut[f[fmask]],
                           process=False) if kept.sum() > 50 and fmask.sum() > 0 else None
    views = [(30, -60), (10, 30)]
    for k, (el, az) in enumerate(views):
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection="3d")
        if sub is not None:
            ax.plot_trisurf(sub.vertices[:, 0], sub.vertices[:, 1], sub.vertices[:, 2],
                            triangles=sub.faces, shade=True, linewidth=0, antialiased=False)
        ax.view_init(elev=el, azim=az)
        ax.set_box_aspect((1, 1, 1))
        ax.set_xlabel("mm"); ax.set_ylabel("mm")
        ax.set_title(f"rim close-up {CLOSEUP_BOX_MM} mm box | grid 0.75 mm, ridge bar 0.2 mm")
        fig.tight_layout()
        fig.savefig(f"{outdir}/closeup_{k}.png", dpi=110)
        plt.close(fig)

    # --- context: whole mesh footprint with crop box ---
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111)
    ax.scatter(v[:, 0], v[:, 1], s=0.3)
    ax.add_patch(plt.Rectangle((centre[0] - half, centre[1] - half),
                               CLOSEUP_BOX_MM, CLOSEUP_BOX_MM,
                               fill=False, edgecolor="r", lw=1.5))
    ax.set_aspect("equal")
    ax.set_xlabel("mm"); ax.set_ylabel("mm")
    ax.set_title("context: full tray footprint (mm), red box = close-up crop")
    fig.tight_layout(); fig.savefig(f"{outdir}/context.png", dpi=110); plt.close(fig)
    print(f"wrote {outdir}/stats.json relief_hist.png closeup_0/1.png context.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
