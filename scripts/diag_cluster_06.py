"""Ticket 06 audit 1 (cluster): re-run the stock post-filter on ONE arm's RAW mesh
with retained-cluster sweeps (keep 10 -> 25 -> all); render the sherd box per
setting. Question: is anything coherent being thrown away, or nothing to keep?

Method: exact replica of render.py post_process_mesh (sort cluster triangle
counts, threshold = kth largest, floor 50). keep=all means no removal.
Box = ticket-04b tight box (centroid + 0.23 units from work/edge_04b/locate.json).
Box faces = faces with all 3 verts in the box (same rule as diag_maskpatch_04).

Renders before numbers: trisurf close-ups of the box submesh per setting at the
same 2 orbit viewpoints as ticket 04, plus a cluster-size chart.
CPU-only (open3d + matplotlib Agg). mm labels PROVISIONAL (A03 scale).

Usage: diag_cluster_06.py <out_root> [A_lama|B_ctrl]  (default A_lama)
"""
import copy
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

MM_PER_UNIT = 373.733  # PROVISIONAL (A03 scale, unproven for A31)
ORBITS = [(30, -60), (10, 30)]
BAR_MM = 20.0
MODELS = {"A_lama": "A31A_lama", "B_ctrl": "A31B_ctrl"}
KEEPS = (10, 25)


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: diag_cluster_06.py <out_root> [A_lama|B_ctrl]", file=sys.stderr)
        return 1
    out_root = sys.argv[1]
    arm = sys.argv[2] if len(sys.argv) > 2 else "A_lama"
    if arm not in MODELS:
        print(f"unknown arm {arm}", file=sys.stderr)
        return 1
    import open3d as o3d

    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")
    prev = json.load(open(f"{pgsr_root}/work/edge_04b/locate.json"))
    X = np.array(prev["centroid_scene_units"])
    box = float(prev["box_scene_units"])
    half = box / 2

    raw_path = f"{pgsr_root}/output/{MODELS[arm]}/mesh/tsdf_fusion.ply"
    print(f"loading {raw_path}", flush=True)
    mesh = o3d.io.read_triangle_mesh(raw_path)
    nv = len(np.asarray(mesh.vertices))
    if nv == 0:
        print("EMPTY MESH", file=sys.stderr)
        return 1
    print(f"raw verts {nv} tris {len(np.asarray(mesh.triangles))}", flush=True)

    with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug):
        tri_cl, cl_n_tri, _ = mesh.cluster_connected_triangles()
    tri_cl = np.asarray(tri_cl)
    cl_n_tri = np.asarray(cl_n_tri)
    order = np.argsort(cl_n_tri)[::-1]
    print(f"n clusters {len(cl_n_tri)}", flush=True)
    print("top30 " + ",".join(str(int(cl_n_tri[i])) for i in order[:30]), flush=True)

    os.makedirs(out_root, exist_ok=True)
    result = {"arm": arm, "centroid": list(X), "box": box,
              "n_clusters": int(len(cl_n_tri)),
              "top30_tri_counts": [int(cl_n_tri[i]) for i in order[:30]],
              "settings": {}}

    # cluster-size chart (log-log), renders before numbers
    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(111)
    ax.loglog(np.arange(1, len(order) + 1), cl_n_tri[order], marker=".", ms=3)
    for k in KEEPS:
        ax.axhline(float(cl_n_tri[order[k - 1]]), ls="--",
                   label=f"keep={k} thr={int(cl_n_tri[order[k-1]])} tris")
    ax.set_xlabel("cluster rank (largest first)")
    ax.set_ylabel("triangles in cluster")
    ax.set_title(f"{arm} raw mesh cluster sizes ({len(cl_n_tri)} clusters)\n"
                 "dashed = retention threshold per keep setting")
    ax.legend()
    fig.savefig(f"{out_root}/cluster_sizes.png", dpi=100)
    plt.close(fig)

    V = np.asarray(mesh.vertices)

    settings = [(10, int(cl_n_tri[order[9]])), (25, int(cl_n_tri[order[24]])),
                ("all", 0)]
    for keep, thr in settings:
        thr = max(thr, 50) if keep != "all" else 0
        tag = f"keep_{keep}"
        if keep == "all":
            m = mesh  # no removal; raw as-is
        else:
            remove = cl_n_tri[tri_cl] < thr
            m = copy.deepcopy(mesh)
            m.remove_triangles_by_mask(remove)
            m.remove_unreferenced_vertices()
            m.remove_degenerate_triangles()
        v = np.asarray(m.vertices)
        f = np.asarray(m.triangles)
        in_box = np.all(np.abs(v - X) < half, axis=1)
        box_idx = np.nonzero(in_box)[0]
        fmask = np.all(in_box[f], axis=1) if len(f) else np.zeros(0, bool)
        n_box, n_faces = int(len(box_idx)), int(fmask.sum())
        # which clusters do the surviving box faces belong to? (recorded once,
        # on the RAW mesh under keep=10 below)
        entry = {"threshold_tris": int(thr), "mesh_verts": int(len(v)),
                 "mesh_tris": int(len(f)), "box_verts": n_box,
                 "box_faces_all3_in": n_faces,
                 "box_faces_per_vert": round(n_faces / n_box, 4) if n_box else 0.0}
        # cluster-id histogram of RAW box faces (arm-independent of setting;
        # recorded once): faces with all 3 verts in box, by their raw cluster
        if keep == 10:
            raw_box = np.nonzero(np.all(np.abs(V - X) < half, axis=1))[0]
            lut = np.full(nv, -1)
            raw_faces = np.asarray(mesh.triangles)
            rfmask = np.all(np.isin(raw_faces, raw_box), axis=1)
            raw_box_cl = tri_cl[rfmask]
            uniq, cnt = np.unique(raw_box_cl, return_counts=True)
            hist = sorted(zip([int(u) for u in uniq], [int(c) for c in cnt]),
                          key=lambda t: -t[1])[:15]
            entry["raw_box_faces"] = int(rfmask.sum())
            entry["raw_box_faces_top_clusters"] = [
                {"cluster": c, "faces": n,
                 "cluster_tris_total": int(cl_n_tri[c]),
                 "rank": int(np.nonzero(order == c)[0][0]) + 1}
                for c, n in hist]
        result["settings"][tag] = entry
        print(f"{tag}: thr={thr} mesh={len(v)}v/{len(f)}f "
              f"box={n_box}v/{n_faces}f", flush=True)

        # --- trisurf renders of the box submesh at both orbits ---
        if n_box > 50 and n_faces > 0:
            kept = np.nonzero(in_box)[0]
            lut = np.full(len(v), -1)
            lut[kept] = np.arange(len(kept))
            import trimesh
            sub = trimesh.Trimesh(vertices=v[kept], faces=lut[f[fmask]],
                                   process=False)
            for k, (el, az) in enumerate(ORBITS):
                fig = plt.figure(figsize=(8.8, 8.8))
                ax = fig.add_subplot(111, projection="3d")
                ax.plot_trisurf(sub.vertices[:, 0], sub.vertices[:, 1],
                                sub.vertices[:, 2], triangles=sub.faces,
                                shade=True, linewidth=0, antialiased=False)
                ax.view_init(elev=el, azim=az)
                ax.set_title(f"{arm} raw {tag}, box {n_box}v/{n_faces}f, "
                             f"el={el} az={az}\n(units x{MM_PER_UNIT:.1f}"
                             "=provisional mm)")
                lo = sub.vertices.min(0)
                ax.plot([lo[0], lo[0] + BAR_MM / MM_PER_UNIT],
                        [lo[1], lo[1]], [lo[2], lo[2]], color="r", lw=3)
                ax.text(lo[0], lo[1], lo[2],
                        f"{BAR_MM:.0f} mm (provisional scale)",
                        color="r", fontsize=10)
                fig.savefig(f"{out_root}/{tag}_tri_{k}.png", dpi=100)
                plt.close(fig)
        else:
            print(f"{tag}: box submesh too small, skipping trisurf", flush=True)

    json.dump(result, open(f"{out_root}/cluster.json", "w"), indent=1)
    print(f"wrote {out_root}/cluster.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
