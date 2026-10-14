"""Ticket 07 reason test (cheap, CPU-only): test two starvation hypotheses
with our own data, no training.

Test A (SfM seed sparsity): densify_and_clone/split only act on EXISTING
points — a Gaussian is cloned/split from a parent, never conjured in empty
space. Count COLMAP sparse seeds inside the ticket-04b tight face box vs six
same-size neighbour boxes (wall/background around the face). Zero/few seeds
at the face = densification has nothing to grow from there.

Test B (image-gradient energy): densification fires on accumulated
view-space positional gradients (train.py:366 add_densification_stats,
thresholds arguments/__init__.py:94,113). A plain clay face gives weak
photometric gradients. Compare mean Sobel energy in the bbox centre-third
(likely face clay) vs the full sherd bbox vs the rest of the frame, on the
six TRAIN face views (1114/1115/1117/1118/1119/1120, control arm).

CPU-only (numpy + PIL + matplotlib Agg; scipy if present, else np.gradient).
mm labels PROVISIONAL (A03 scale).
Usage: diag_reason_07.py <out_root>
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "preprocess"))
import read_write_model as rwm

MM_PER_UNIT = 373.733  # PROVISIONAL (A03 scale, unproven for A31)
FACE_VIEWS = ["A31_1114.JPG", "A31_1115.JPG", "A31_1117.JPG",
              "A31_1118.JPG", "A31_1119.JPG", "A31_1120.JPG"]
try:
    from scipy.ndimage import sobel as _sobel
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


def grad_energy(gray):
    g = gray.astype(np.float64)
    if HAVE_SCIPY:
        gx = _sobel(g, axis=1)
        gy = _sobel(g, axis=0)
    else:
        gy, gx = np.gradient(g)
    return np.sqrt(gx ** 2 + gy ** 2)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: diag_reason_07.py <out_root>", file=sys.stderr)
        return 1
    out_root = sys.argv[1]
    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")
    prev = json.load(open(f"{pgsr_root}/work/edge_04b/locate.json"))
    X = np.array(prev["centroid_scene_units"])
    box = float(prev["box_scene_units"])
    half = box / 2
    os.makedirs(out_root, exist_ok=True)
    result = {"centroid": list(X), "box": box,
              "scipy": HAVE_SCIPY, "seed": {}, "gradient": {}}

    # ---- Test A: SfM seed density (control sparse; geometry shared) ----
    pts = rwm.read_points3D_binary(
        f"{pgsr_root}/data/17062025/A31_control/sparse/points3D.bin")
    xyz = np.stack([p.xyz for p in pts.values()])
    print(f"seed: n_total={len(xyz)}", flush=True)
    shifts = {"face": np.zeros(3),
              "px": np.array([box, 0, 0]), "nx": np.array([-box, 0, 0]),
              "py": np.array([0, box, 0]), "ny": np.array([0, -box, 0]),
              "pz": np.array([0, 0, box]), "nz": np.array([0, 0, -box])}
    counts = {}
    for name, sh in shifts.items():
        c = X + sh
        inside = (np.abs(xyz - c) <= half).all(axis=1)
        counts[name] = int(inside.sum())
    dc = np.linalg.norm(xyz - X, axis=1)
    near = np.argsort(dc)[:10]
    result["seed"] = {
        "n_total": int(len(xyz)),
        "box_counts": counts,
        "nearest10_centroid_dist_units":
            [round(float(v), 6) for v in dc[near]],
        "nearest10_centroid_dist_provmm":
            [round(float(v) * MM_PER_UNIT, 2) for v in dc[near]],
    }
    print(f"seed: box_counts={counts} nearest={dc[near[0]]:.6f}u "
          f"({dc[near[0]] * MM_PER_UNIT:.1f} prov-mm)", flush=True)

    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(list(counts), list(counts.values()))
    ax.set_title("SfM seeds per face-size box (control sparse)")
    ax.set_ylabel("points")
    fig.tight_layout()
    fig.savefig(f"{out_root}/seed_counts.png", dpi=80)
    plt.close(fig)

    # ---- Test B: gradient energy (control images, native coords) ----
    track = json.load(open(
        f"{pgsr_root}/lama_trial/ticket03/face_survey/track_true.json"))
    imgdir = f"{pgsr_root}/data/17062025/A31_control/images"
    pictured = 0
    for view in FACE_VIEWS:
        im = Image.open(os.path.join(imgdir, view)).convert("L")
        W, H = im.size
        sx, sy = W / 5568.0, H / 3712.0  # native 5568x3712 bbox coords
        x0, y0, x1, y1 = track[view]["bbox"]
        x0, y0, x1, y1 = (int(x0 * sx), int(y0 * sy),
                          int(x1 * sx), int(y1 * sy))
        g = np.asarray(im)
        E = grad_energy(g)
        bw, bh = x1 - x0, y1 - y0
        core = E[y0 + bh // 3:y0 + 2 * bh // 3, x0 + bw // 3:x0 + 2 * bw // 3]
        sbox = E[y0:y1, x0:x1]
        mask = np.ones_like(E, bool)
        mask[y0:y1, x0:x1] = False
        entry = {
            "image_size": [W, H],
            "bbox_scaled": [x0, y0, x1, y1],
            "mean_core": round(float(core.mean()), 4),
            "mean_bbox": round(float(sbox.mean()), 4),
            "mean_rest": round(float(E[mask].mean()), 4),
        }
        result["gradient"][view] = entry
        print(f"grad {view}: core={entry['mean_core']:.3f} "
              f"bbox={entry['mean_bbox']:.3f} rest={entry['mean_rest']:.3f}",
              flush=True)
        if pictured < 2:
            fig, ax = plt.subplots(1, 2, figsize=(12, 5))
            ax[0].imshow(g[y0:y1, x0:x1], cmap="gray")
            ax[0].add_patch(plt.Rectangle(
                (bw // 3, bh // 3), bw // 3, bh // 3,
                fill=False, edgecolor="red", linewidth=2))
            ax[0].set_title(f"{view} sherd bbox (red = core)")
            ax[1].imshow(E[y0:y1, x0:x1], cmap="hot")
            ax[1].set_title("Sobel energy in bbox")
            fig.tight_layout()
            fig.savefig(f"{out_root}/grad_{view[:-4]}.png", dpi=80)
            plt.close(fig)
            pictured += 1

    json.dump(result, open(f"{out_root}/reason.json", "w"), indent=1)
    print("wrote reason.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
