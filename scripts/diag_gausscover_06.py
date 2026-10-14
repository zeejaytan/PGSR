"""Ticket 06 audit 2b (gaussian coverage follow-up): centre-counts understate
coverage — a fat Gaussian centred outside the box can still cover it. Per arm:
for every trained Gaussian, distance from its centre to the sherd box (0 if
inside) in units of its own mean footprint; count covering (dist < 3*fp);
nearest-10 centre distances to the centroid. Decides whether the face has ANY
Gaussian cover, however thin.

CPU-only (numpy + matplotlib Agg). mm labels PROVISIONAL (A03 scale).
Usage: diag_gausscover_06.py <out_root>
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

MM_PER_UNIT = 373.733  # PROVISIONAL (A03 scale, unproven for A31)
ARMS = (("A_lama", "A31A_lama"), ("B_ctrl", "A31B_ctrl"))


def read_xyz_fp(path):
    with open(path, "rb") as fh:
        head = fh.read(1024 * 1024).split(b"\n")
        end = next(i for i, l in enumerate(head) if l.strip() == b"end_header")
        props, n = [], 0
        for l in head[:end]:
            p = l.decode("ascii", "replace").split()
            if len(p) == 3 and p[0] == "element" and p[1] == "vertex":
                n = int(p[2])
            elif len(p) == 3 and p[0] == "property":
                props.append(p[2])
        fh.seek(sum(len(l) + 1 for l in head[:end + 1]))
        raw = np.fromfile(fh, dtype=np.float32, count=n * len(props))
        assert raw.size == n * len(props), f"short read {path}"
        raw = raw.reshape(n, len(props))
        d = {name: raw[:, i] for i, name in enumerate(props)}
    xyz = np.stack([d["x"], d["y"], d["z"]], 1)
    fp = np.exp(np.stack([d["scale_0"], d["scale_1"], d["scale_2"]], 1)).mean(1)
    return xyz, fp


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: diag_gausscover_06.py <out_root>", file=sys.stderr)
        return 1
    out_root = sys.argv[1]
    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")
    prev = json.load(open(f"{pgsr_root}/work/edge_04b/locate.json"))
    X = np.array(prev["centroid_scene_units"])
    box = float(prev["box_scene_units"])
    half = box / 2
    os.makedirs(out_root, exist_ok=True)
    result = {"centroid": list(X), "box": box, "arms": {}}

    fig = plt.figure(figsize=(12, 5))
    for j, (arm, model) in enumerate(ARMS):
        xyz, fp = read_xyz_fp(
            f"{pgsr_root}/output/{model}/point_cloud/iteration_30000/point_cloud.ply")
        # distance from centre to box surface (0 inside), in footprint units
        dbox = np.abs(xyz - X) - half
        dbox = np.where(dbox < 0, 0, dbox)
        dist = np.linalg.norm(dbox, axis=1)
        sigma = np.where(fp > 0, dist / fp, np.inf)
        covering = int((sigma < 3).sum())
        dc = np.linalg.norm(xyz - X, axis=1)
        near = np.argsort(dc)[:10]
        entry = {
            "n_total": int(len(xyz)),
            "n_covering_3sigma": covering,
            "nearest10_centroid_dist_units": [round(float(v), 6) for v in dc[near]],
            "nearest10_centroid_dist_provmm": [round(float(v) * MM_PER_UNIT, 2) for v in dc[near]],
            "nearest10_footprint_units": [round(float(v), 6) for v in fp[near]],
        }
        result["arms"][arm] = entry
        print(f"{arm}: covering3sigma={covering} nearest={dc[near[0]]:.6f}u "
              f"({dc[near[0]] * MM_PER_UNIT:.1f} prov-mm)", flush=True)
        ax = fig.add_subplot(1, 2, j + 1)
        ax.hist(np.clip(dc, 0, 1.0), bins=100)
        ax.axvline(half, color="r", ls="--", label=f"box half-edge {half}u")
        ax.set_xlabel("centre distance to centroid, scene units (clipped 1.0)")
        ax.set_ylabel("count")
        ax.set_title(f"{arm}: {covering} Gaussians cover box at 3-sigma")
        ax.legend()
        del xyz, fp, dist, sigma, dc
    fig.tight_layout()
    fig.savefig(f"{out_root}/cover_hist.png", dpi=110)
    plt.close(fig)
    json.dump(result, open(f"{out_root}/cover.json", "w"), indent=1)
    print(f"wrote {out_root}/cover.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
