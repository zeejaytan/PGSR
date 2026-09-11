#!/usr/bin/env python3
"""Report mesh stats for the PGSR A/B trial: verts, tris, cluster sizes, bounds.

Usage (on a node holding the allocation, any CPU):
    python scripts/mesh_stats.py <mesh_dir> [<mesh_dir> ...]
Refuses loudly on an unreadable mesh instead of printing a partial table.
"""
from __future__ import annotations

import sys

import numpy as np


def main() -> int:
    import open3d as o3d

    if len(sys.argv) < 2:
        print("usage: mesh_stats.py <mesh_dir> [...]", file=sys.stderr)
        return 1
    rc = 0
    for d in sys.argv[1:]:
        for f in ("tsdf_fusion.ply", "tsdf_fusion_post.ply"):
            p = f"{d}/{f}"
            try:
                m = o3d.io.read_triangle_mesh(p)
            except Exception as e:  # noqa: BLE001
                print(f"{p}: READ FAIL {e}"[:160])
                rc = 1
                continue
            vtx = np.asarray(m.vertices)
            tri = np.asarray(m.triangles)
            if len(vtx) == 0:
                print(f"{p}: EMPTY MESH")
                rc = 1
                continue
            _, n, _ = m.cluster_connected_triangles()
            n = np.asarray(n)
            span = (vtx.max(0) - vtx.min(0)).round(4)
            print(
                f"{p}: verts {len(vtx)} tris {len(tri)} "
                f"clusters {len(n)} top5 {sorted(n)[-5:]} span {list(span)}"
            )
    return rc


if __name__ == "__main__":
    sys.exit(main())
