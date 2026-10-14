#!/usr/bin/env python3
"""Slab test (ticket 04): is the box content a thin face slab or volume noise?
Numbers (z-quantiles, thickness) + one z-coloured x-z scatter per arm on the
RAW mesh. Usage: diag_slab_04.py <outdir>
"""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

X = np.array([-0.1812, 0.4883, -0.1933])
BOX = 0.400
MM = 373.733  # PROVISIONAL scale, labels only


def main() -> int:
    import trimesh

    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")
    for arm, model in (("A_lama", "A31A_lama"), ("B_ctrl", "A31B_ctrl")):
        v = np.asarray(trimesh.load(
            f"{pgsr_root}/output/{model}/mesh/tsdf_fusion.ply",
            process=False).vertices, dtype=np.float64)
        box = v[np.all(np.abs(v - X) < BOX / 2, axis=1)]
        z = box[:, 2]
        print(f"{arm}: box n={len(box)} z-min={z.min():.4f} z-max={z.max():.4f} "
              f"z-q10={np.quantile(z,0.1):.4f} z-q50={np.quantile(z,0.5):.4f} "
              f"z-q90={np.quantile(z,0.9):.4f} thickness10-90="
              f"{(np.quantile(z,0.9)-np.quantile(z,0.1))*MM:.1f}mm-prov", flush=True)
        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(111)
        sc = ax.scatter(box[::3, 0] * MM, box[::3, 2] * MM, s=1,
                        c=box[::3, 2] * MM, cmap="coolwarm")
        ax.scatter([X[0] * MM], [X[2] * MM], s=150, c="g", marker="*")
        fig.colorbar(sc, label="z mm (provisional)")
        ax.set_aspect("equal")
        ax.set_xlabel("x mm (provisional)")
        ax.set_ylabel("z mm (provisional)")
        ax.set_title(f"{arm} RAW box content x-z, z-coloured (mm provisional)")
        fig.tight_layout()
        fig.savefig(f"{outdir}/{arm}_slab_xz.png", dpi=110)
        plt.close(fig)
        print(f"{arm}: wrote slab view", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
