#!/usr/bin/env python3
"""Raw-mesh check (ticket 04 follow-up): (1) COLMAP-frame vs train-frame test
(C0 from images.bin vs cameras.json position for A31_1100); (2) verts-in-box
around X in the RAW pre-post-filter mesh per arm. Numbers to stdout. CPU-only.
Usage: python scripts/diag_raw_04.py
"""
from __future__ import annotations

import json
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

    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")
    imgs = read_images(f"{pgsr_root}/data/17062025/A31_control/sparse/images.bin")
    q, t = imgs["A31_1100.JPG"]
    C = -qvec_to_R(q).T @ t
    cj = json.load(open(f"{pgsr_root}/output/A31A_lama/cameras.json"))
    e0 = [e for e in cj if e.get("img_name") == "A31_1100"][0]
    print(f"COLMAP C(A31_1100) = {C.round(4)}", flush=True)
    print(f"cameras.json pos   = {np.array(e0['position']).round(4)}", flush=True)
    for arm, model in (("A_lama", "A31A_lama"), ("B_ctrl", "A31B_ctrl")):
        v = np.asarray(trimesh.load(
            f"{pgsr_root}/output/{model}/mesh/tsdf_fusion.ply",
            process=False).vertices, dtype=np.float64)
        print(f"{arm} RAW verts={len(v)} bbox={v.min(0).round(3)}/{v.max(0).round(3)}",
              flush=True)
        for half in (0.2, 0.5, 1.0):
            n = int(np.all(np.abs(v - X) < half, axis=1).sum())
            print(f"{arm} RAW verts in {half}u box: {n}", flush=True)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
