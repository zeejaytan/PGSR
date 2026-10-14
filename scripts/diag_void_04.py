#!/usr/bin/env python3
"""Probe the void: nearest mesh vertex to X, z-profile of mesh verts in the
x-y neighbourhood of X, and COLMAP camera-centre distances (scale sanity).
Usage: python scripts/diag_void_04.py
"""
from __future__ import annotations

import os
import struct

import numpy as np

X = np.array([-0.1812, 0.4883, -0.1933])


def read_images(path: str):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        out = {}
        for _ in range(n):
            img_id = struct.unpack("<I", fh.read(4))[0]
            qvec = struct.unpack("<4d", fh.read(32))
            tvec = struct.unpack("<3d", fh.read(24))
            cam_id = struct.unpack("<I", fh.read(4))[0]
            name = b""
            while True:
                ch = fh.read(1)
                if ch == b"\x00":
                    break
                name += ch
            n2d = struct.unpack("<Q", fh.read(8))[0]
            fh.read(n2d * 24)
            out[name.decode()] = (np.array(qvec), np.array(tvec))
    return out


def qvec_to_R(q):
    qw, qx, qy, qz = q
    n = qw * qw + qx * qx + qy * qy + qz * qz
    s = 2.0 / n if n > 0 else 0.0
    return np.array([
        [1 - s * (qy * qy + qz * qz), s * (qx * qy - qw * qz), s * (qx * qz + qw * qy)],
        [s * (qx * qy + qw * qz), 1 - s * (qx * qx + qz * qz), s * (qy * qz - qw * qx)],
        [s * (qx * qz - qw * qy), s * (qy * qz + qw * qx), 1 - s * (qx * qx + qy * qy)],
    ])


def main() -> int:
    import trimesh
    from scipy.spatial import cKDTree

    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")
    imgs = read_images(f"{pgsr_root}/data/17062025/A31_control/sparse/images.bin")
    print("camera centres (|C|, distance to X):", flush=True)
    for name in ["A31_1114.JPG", "A31_1116.JPG", "A31_1117.JPG", "A31_1120.JPG"]:
        q, t = imgs[name]
        C = -qvec_to_R(q).T @ t
        print(f"  {name}: |C|={np.linalg.norm(C):.3f} |C-X|={np.linalg.norm(C-X):.3f} "
              f"C={C.round(3)}", flush=True)
    for arm, model in (("A_lama", "A31A_lama"), ("B_ctrl", "A31B_ctrl")):
        v = np.asarray(trimesh.load(
            f"{pgsr_root}/output/{model}/mesh/tsdf_fusion_post.ply",
            process=False).vertices, dtype=np.float64)
        tree = cKDTree(v)
        d, j = tree.query(X)
        print(f"{arm}: nearest to X: d={d:.4f}u at {v[j].round(4)}", flush=True)
        for half in (0.2, 0.5, 1.0):
            n = int(np.all(np.abs(v - X) < half, axis=1).sum())
            print(f"{arm}: verts in {half}u box: {n}", flush=True)
        # z-profile of verts in the x-y column around X (1.0u half-width in x,y)
        col = v[(np.abs(v[:, 0] - X[0]) < 1.0) & (np.abs(v[:, 1] - X[1]) < 1.0)]
        if len(col):
            qs = np.quantile(col[:, 2], [0, 0.1, 0.5, 0.9, 1.0])
            print(f"{arm}: x-y column n={len(col)} z-quantiles={qs.round(3)} Xz={X[2]:.3f}",
                  flush=True)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
