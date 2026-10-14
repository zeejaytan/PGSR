#!/usr/bin/env python3
"""See the void: side-view scatters of mesh + sparse points around X, and a
cameras.json-vs-images.bin transform check. Usage: diag_see_04.py <outdir>
"""
from __future__ import annotations

import json
import os
import struct

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

X = np.array([-0.1812, 0.4883, -0.1933])
MM = 373.733  # PROVISIONAL scale, labels only


def read_points(path: str):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        pts = np.empty((n, 3))
        for i in range(n):
            fh.read(8)
            pts[i] = struct.unpack("<3d", fh.read(24))
            fh.read(3)
            fh.read(8)
            trlen = struct.unpack("<Q", fh.read(8))[0]
            fh.read(trlen * 8)
    return pts


def main() -> int:
    import sys
    import trimesh

    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")

    pts = read_points(f"{pgsr_root}/data/17062025/A31_control/sparse/points3D.bin")
    near = pts[np.linalg.norm(pts - X, axis=1) < 1.5]
    print(f"sparse pts within 1.5u of X: {len(near)}", flush=True)
    for r in (0.2, 0.5):
        print(f"sparse pts within {r}u of X: {int((np.linalg.norm(pts-X,axis=1)<r).sum())}",
              flush=True)

    # cameras.json (as used by train) vs COLMAP: same frame?
    cj = json.load(open(f"{pgsr_root}/output/A31A_lama/cameras.json"))
    print(f"cameras.json type={type(cj).__name__} len={len(cj)}", flush=True)
    first = cj[0] if isinstance(cj, list) else cj[list(cj.keys())[0]]
    print("first entry: " + json.dumps(first)[:400], flush=True)

    for arm, model in (("A_lama", "A31A_lama"), ("B_ctrl", "A31B_ctrl")):
        v = np.asarray(trimesh.load(
            f"{pgsr_root}/output/{model}/mesh/tsdf_fusion_post.ply",
            process=False).vertices, dtype=np.float64)
        col = v[(np.abs(v[:, 0] - X[0]) < 1.0) & (np.abs(v[:, 1] - X[1]) < 1.0)]
        for (a, b, lab) in ((0, 2, "x-z"), (1, 2, "y-z")):
            fig = plt.figure(figsize=(9, 7))
            ax = fig.add_subplot(111)
            ax.scatter(col[::10, a] * MM, col[::10, b] * MM, s=0.5, label="mesh")
            if len(near):
                ax.scatter(near[:, a] * MM, near[:, b] * MM, s=6, c="r", label="sparse")
            ax.scatter([X[a] * MM], [X[b] * MM], s=120, c="g", marker="*",
                       label="triangulated X")
            ax.set_aspect("equal")
            ax.set_xlabel(f"{'x' if a==0 else 'y'} mm (provisional)")
            ax.set_ylabel("z mm (provisional)")
            ax.legend()
            ax.set_title(f"{arm} {lab} side view near X (mm provisional)")
            fig.tight_layout()
            fig.savefig(f"{outdir}/{arm}_{lab}.png", dpi=110)
            plt.close(fig)
        print(f"{arm}: wrote side views", flush=True)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
