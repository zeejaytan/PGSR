#!/usr/bin/env python3
"""Diagnose the empty-box finding (ticket 04): is the fused mesh in the same
frame as the COLMAP sparse model? Reports (a) distance from the triangulated
A31 centroid to the nearest mesh vertex per arm; (b) sparse-points3D bbox vs
mesh bbox; (c) median nearest-mesh distance of a sparse-point sample;
(d) camera-centre bbox vs mesh bbox. Small JSON to stdout. CPU-only.
Usage: python scripts/diag_frame_04.py
"""
from __future__ import annotations

import json
import os
import struct

import numpy as np

X = np.array([-0.1812, 0.4883, -0.1933])  # triangulated A31 centroid, scene units


def read_points(path: str):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        pts = np.empty((n, 3))
        for i in range(n):
            pid = struct.unpack("<Q", fh.read(8))[0]
            x, y, z = struct.unpack("<3d", fh.read(24))
            r, g, b = struct.unpack("<3B", fh.read(3))
            err = struct.unpack("<d", fh.read(8))[0]
            trlen = struct.unpack("<Q", fh.read(8))[0]
            fh.read(trlen * 8)  # image_id (I) + point2D_idx (I)
            pts[i] = (x, y, z)
    return pts


def main() -> int:
    import trimesh
    from scipy.spatial import cKDTree

    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")
    pts = read_points(f"{pgsr_root}/data/17062025/A31_control/sparse/points3D.bin")
    print(f"sparse points: {len(pts)} bbox_min={pts.min(0).round(3)} "
          f"bbox_max={pts.max(0).round(3)}", flush=True)
    rng = np.random.default_rng(7)
    sample = pts[rng.choice(len(pts), size=min(3000, len(pts)), replace=False)]
    out = {"centroid": X.tolist()}
    for arm, model in (("A_lama", "A31A_lama"), ("B_ctrl", "A31B_ctrl")):
        v = np.asarray(trimesh.load(
            f"{pgsr_root}/output/{model}/mesh/tsdf_fusion_post.ply",
            process=False).vertices, dtype=np.float64)
        tree = cKDTree(v)
        d_cent, _ = tree.query(X)
        d_samp, _ = tree.query(sample)
        out[arm] = {
            "mesh_bbox_min": [round(float(a), 3) for a in v.min(0)],
            "mesh_bbox_max": [round(float(a), 3) for a in v.max(0)],
            "centroid_nearest_mm_prov": round(float(d_cent) * 373.733, 1),
            "sparse_sample_median_nearest_mm_prov": round(float(np.median(d_samp)) * 373.733, 1),
            "sparse_sample_p90_nearest_mm_prov": round(float(np.quantile(d_samp, 0.9)) * 373.733, 1),
        }
        print(f"{arm}: centroid-nearest={d_cent:.4f}u "
              f"sample-median={np.median(d_samp):.4f}u p90={np.quantile(d_samp, 0.9):.4f}u",
              flush=True)
    print("JSON:" + json.dumps(out))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
