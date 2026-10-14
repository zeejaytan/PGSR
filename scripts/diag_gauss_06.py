"""Ticket 06 audit 2 (gaussian): count trained Gaussians inside the sherd box per
arm + footprint stats from the trained scenes. Question: does the failure start
upstream of fusion (face under-parameterised)?

Reads output/<model>/point_cloud/iteration_30000/point_cloud.ply directly
(xyz + opacity + scale_0/1/2 log-scales). Box = ticket-04b tight box
(centroid + 0.23 units from work/edge_04b/locate.json).
Footprint = exp(scale) per axis, mean over axes; reported in scene units and
PROVISIONAL mm (A03 373.733 scale, unproven for A31).

Renders before numbers: scatter close-ups of in-box Gaussian centres per arm
(same 2 orbits as ticket 04) + footprint histograms (in-box vs global).
CPU-only (numpy + matplotlib Agg).

Usage: diag_gauss_06.py <out_root>
"""
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
ARMS = (("A_lama", "A31A_lama"), ("B_ctrl", "A31B_ctrl"))


def read_ply(path):
    """Generic little-endian float32 PLY reader -> dict of float32 arrays."""
    with open(path, "rb") as fh:
        props = []
        line = fh.read(1024 * 1024)  # header fits well within 1MB
        lines = line.split(b"\n")
        end = next(i for i, l in enumerate(lines) if l.strip() == b"end_header")
        n_vert = 0
        for l in lines[:end]:
            p = l.decode("ascii", "replace").split()
            if len(p) == 3 and p[0] == "element" and p[1] == "vertex":
                n_vert = int(p[2])
            elif len(p) == 3 and p[0] == "property" and p[1] == "float":
                props.append(p[2])
        off = sum(len(l) + 1 for l in lines[:end + 1])
        fh.seek(off)
        raw = np.fromfile(fh, dtype=np.float32, count=n_vert * len(props))
        if raw.size != n_vert * len(props):
            raise ValueError(f"short read {path}: {raw.size} vs {n_vert * len(props)}")
        raw = raw.reshape(n_vert, len(props))
    return {name: raw[:, i] for i, name in enumerate(props)}


def q(vals):
    vals = np.asarray(vals, float)
    return [round(float(v), 6) for v in np.percentile(vals, [0, 5, 50, 95, 100])]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: diag_gauss_06.py <out_root>", file=sys.stderr)
        return 1
    out_root = sys.argv[1]
    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")
    prev = json.load(open(f"{pgsr_root}/work/edge_04b/locate.json"))
    X = np.array(prev["centroid_scene_units"])
    box = float(prev["box_scene_units"])
    half = box / 2
    os.makedirs(out_root, exist_ok=True)
    result = {"centroid": list(X), "box": box, "arms": {}}

    for arm, model in ARMS:
        p = f"{pgsr_root}/output/{model}/point_cloud/iteration_30000/point_cloud.ply"
        print(f"reading {p}", flush=True)
        d = read_ply(p)
        xyz = np.stack([d["x"], d["y"], d["z"]], 1)
        fp = np.exp(np.stack([d["scale_0"], d["scale_1"], d["scale_2"]], 1)).mean(1)
        op = 1.0 / (1.0 + np.exp(-d["opacity"]))  # sigmoid
        in_box = np.all(np.abs(xyz - X) < half, axis=1)
        n_in = int(in_box.sum())
        entry = {"n_total": int(len(xyz)), "n_in_box": n_in,
                 "frac_in_box": round(n_in / len(xyz), 8),
                 "footprint_units_p0_p5_p50_p95_p100": q(fp),
                 "footprint_inbox_units_p0_p5_p50_p95_p100": q(fp[in_box]) if n_in else [],
                 "footprint_inbox_provmm_p50_p95": [round(float(np.median(fp[in_box])) * MM_PER_UNIT, 3),
                                                   round(float(np.percentile(fp[in_box], 95)) * MM_PER_UNIT, 3)] if n_in else [],
                 "opacity_p0_p5_p50_p95_p100": q(op),
                 "opacity_inbox_p0_p5_p50_p95_p100": q(op[in_box]) if n_in else []}
        result["arms"][arm] = entry
        print(f"{arm}: total={len(xyz)} inbox={n_in} "
              f"fp_med={np.median(fp):.6f} fp_inbox_med="
              f"{np.median(fp[in_box]):.6f}" if n_in else f"{arm}: EMPTY BOX",
              flush=True)

        # --- scatter close-ups of in-box centres, both orbits ---
        if n_in > 10:
            pts = xyz[in_box]
            step = max(1, n_in // 6000)
            for k, (el, az) in enumerate(ORBITS):
                fig = plt.figure(figsize=(8.8, 8.8))
                ax = fig.add_subplot(111, projection="3d")
                ax.scatter(pts[::step, 0], pts[::step, 1], pts[::step, 2],
                           c=pts[::step, 2], s=1, cmap="viridis")
                ax.view_init(elev=el, azim=az)
                ax.set_title(f"{arm} trained Gaussians in box "
                             f"({n_in}/{len(xyz)}), el={el} az={az}\n"
                             f"(units x{MM_PER_UNIT:.1f}=provisional mm)")
                lo = pts.min(0)
                ax.plot([lo[0], lo[0] + BAR_MM / MM_PER_UNIT],
                        [lo[1], lo[1]], [lo[2], lo[2]], color="r", lw=3)
                ax.text(lo[0], lo[1], lo[2],
                        f"{BAR_MM:.0f} mm (provisional scale)",
                        color="r", fontsize=10)
                fig.savefig(f"{out_root}/{arm}_gauss_{k}.png", dpi=100)
                plt.close(fig)
            # --- footprint histogram: in-box vs global ---
            fig = plt.figure(figsize=(9, 6))
            ax = fig.add_subplot(111)
            ax.hist(fp, bins=80, alpha=0.5, label=f"global (n={len(fp)})")
            ax.hist(fp[in_box], bins=80, alpha=0.7,
                    label=f"in-box (n={n_in})")
            ax.set_xlim(0, float(np.percentile(fp, 99.5)))
            ax.set_xlabel("mean footprint exp(scale), scene units")
            ax.set_ylabel("count")
            ax.set_title(f"{arm} Gaussian footprint: in-box vs global")
            ax.legend()
            fig.savefig(f"{out_root}/{arm}_footprint.png", dpi=100)
            plt.close(fig)

    json.dump(result, open(f"{out_root}/gauss.json", "w"), indent=1)
    print(f"wrote {out_root}/gauss.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
