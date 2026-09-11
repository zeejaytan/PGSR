#!/usr/bin/env python3
"""Does render.py fuse through the camera pose or its inverse?

Reproduces render.py's fusion pose construction exactly (pose[:3,:3] =
view.R.T, pose[:3,3] = view.T) and asks, for a real view, where COLMAP-frame
sparse points land when that pose is treated as Open3D expects
(camera-to-world) versus the true COLMAP projection (control).

If the control centers points in-frame while the fusion-assumed camera throws
them out of frame, the extracted mesh was fused through an inverted pose and
lives in the wrong frame. Refuses loudly on missing inputs.
"""
from __future__ import annotations

import argparse
import sys

import numpy as np


def qvec2rotmat(qvec):
    w, x, y, z = qvec
    return np.array(
        [
            [1 - 2 * x**2 - 2 * z**2, 2 * x * y - 2 * z * w, 2 * x * z + 2 * y * w],
            [2 * x * y + 2 * z * w, 1 - 2 * y**2 - 2 * z**2, 2 * y * z - 2 * x * w],
            [2 * x * z - 2 * y * w, 2 * y * z + 2 * x * w, 1 - 2 * x**2 - 2 * y**2],
        ]
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sparse-bin", required=True, help="COLMAP images.bin")
    ap.add_argument("--points-ply", required=True, help="COLMAP-frame points")
    ap.add_argument("--fx", type=float, required=True)
    ap.add_argument("--fy", type=float, required=True)
    ap.add_argument("--w", type=int, required=True)
    ap.add_argument("--h", type=int, required=True)
    args = ap.parse_args()

    sys.path.insert(0, "/data/gpfs/projects/punim2657/PGSR/repo")
    from scene.colmap_loader import read_extrinsics_binary  # noqa: E402
    from plyfile import PlyData  # noqa: E402

    extr = read_extrinsics_binary(args.sparse_bin)
    key = sorted(extr.keys())[len(extr) // 2]
    e = extr[key]
    R_w2c = qvec2rotmat(e.qvec)
    t = np.array(e.tvec)

    # render.py's construction: view.R is stored transposed, pose un-transposes
    view_R = R_w2c.T
    pose = np.identity(4)
    pose[:3, :3] = view_R.transpose(-1, -2)
    pose[:3, 3] = t

    K = np.array([[args.fx, 0, args.w / 2], [0, args.fy, args.h / 2], [0, 0, 1]])
    ply = PlyData.read(args.points_ply)
    P = np.stack([ply["vertex"][a] for a in "xyz"], -1).astype(float)
    P = P[np.linalg.norm(P, axis=1) < 10]  # scene-scale points only

    def frac_in_frame(R, tt, label):
        cam = (R @ P.T + tt[:, None]).T
        ok = cam[:, 2] > 0
        uv = (K @ cam[ok].T).T
        uv = uv[:, :2] / uv[:, 2:3]
        inside = ((uv[:, 0] >= 0) & (uv[:, 0] < args.w) & (uv[:, 1] >= 0) & (uv[:, 1] < args.h)).mean()
        print(f"{label}: {inside:.1%} of {ok.sum()} forward points inside frame")
        return inside

    control = frac_in_frame(R_w2c, t, "control COLMAP P=K[R|t]      ")
    # Open3D treats `pose` as camera-to-world, so the camera render.py fused
    # under is P_fused = K @ inv(pose)
    fused = frac_in_frame(np.linalg.inv(pose)[:3, :3], np.linalg.inv(pose)[:3, 3], "fusion-assumed P=K[inv(pose)]")
    if control > 0.5 and fused < 0.5:
        print("VERDICT: fusion pose is inverted relative to COLMAP — mesh is in the wrong frame")
    elif fused > 0.5 and control < 0.5:
        print("VERDICT: unexpected — control fails, check inputs")
    else:
        print("VERDICT: inconclusive from this view")
    return 0


if __name__ == "__main__":
    sys.exit(main())
