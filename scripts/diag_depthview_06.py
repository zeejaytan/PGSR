"""Ticket 06 audit 3 (depth-view): at the face views, how many views constrain the
face vs arrive clamp-occluded? Rendered depth crops + per-view contributions.

CPU-only, no GPU re-render. Inputs: shared 33-camera sparse model, track
masks (track_true.json bboxes), the TRAIN-view JET depth maps saved at
extraction (output/<model>/train/ours_30000/renders_depth/, 28 views), and
the ticket-04b centroid+box. Per-view geometric contribution = project the
centroid: front? in-frame? inside the A31 mask bbox? train or llffhold-test?
Clamp-occlusion px counts at 1114-1120 are cited from the ticket-03 eye survey
(face_survey, jawlike rule) — not re-derived here.

Key check: A31_1116 is an llffhold test view (idx 16 of sorted 33), so it has
no renders_depth file and never contributed a depth map to fusion.

Outputs: depthview.json (per-view table) + JET depth crops centred on the
projected centroid for the 6 TRAIN face views + a coverage bar chart.
mm labels PROVISIONAL (A03 scale).

Usage: diag_depthview_06.py <out_root>
"""
import json
import os
import struct
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

NATIVE_OVER_SPARSE = 5568.0 / 3200.0
FACE_VIEWS = [f"A31_{n}.JPG" for n in (1114, 1115, 1116, 1117, 1118, 1119, 1120)]
CROP = 200  # half-size px (s3200 frame) of the depth crop square
# ticket-03 face_survey jawlike-occlusion px inside A31 bbox (conservative
# lower bound; lum<90 & |R-B|<15 with >50% pale-face neighbourhood rule)
OCCLUDE_PX = {"A31_1114.JPG": 23, "A31_1115.JPG": 276, "A31_1116.JPG": 419,
              "A31_1117.JPG": 436, "A31_1118.JPG": 404, "A31_1119.JPG": 343,
              "A31_1120.JPG": 87}


def read_cameras(path):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        out = {}
        for _ in range(n):
            cid = struct.unpack("<I", fh.read(4))[0]
            model = struct.unpack("<I", fh.read(4))[0]
            w = struct.unpack("<Q", fh.read(8))[0]
            h = struct.unpack("<Q", fh.read(8))[0]
            npar = {0: 3, 1: 4, 2: 5, 3: 4, 4: 8, 5: 12,
                    6: 5, 7: 5, 8: 4, 9: 5, 10: 12, 11: 12}[model]
            out[cid] = (model, w, h, struct.unpack(f"<{npar}d", fh.read(8 * npar)))
        return out


def read_images(path):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        imgs = {}
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
            imgs[name.decode()] = (img_id, qvec, tvec, cam_id)
    return imgs


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
    if len(sys.argv) != 2:
        print("usage: diag_depthview_06.py <out_root>", file=sys.stderr)
        return 1
    out_root = sys.argv[1]
    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")
    prev = json.load(open(f"{pgsr_root}/work/edge_04b/locate.json"))
    X = np.array(prev["centroid_scene_units"])
    track = json.load(open(f"{pgsr_root}/lama_trial/ticket03/face_survey/track_true.json"))

    sparse_dir = f"{pgsr_root}/data/17062025/A31_control/sparse"
    cams = read_cameras(f"{sparse_dir}/cameras.bin")
    imgs = read_images(f"{sparse_dir}/images.bin")
    model_id, w, h, params = cams[1]
    assert (model_id, w, h) == (1, 3200, 2133), f"unexpected camera {(model_id, w, h)}"
    fx, fy, cx, cy = params

    names = sorted(imgs)
    assert len(names) == 33 and names[0] == "A31_1100.JPG", names[:3]
    test_idx = {0, 8, 16, 24, 32}
    test_names = {names[i] for i in test_idx}
    print(f"test views (llffhold=8): {sorted(test_names)}", flush=True)

    os.makedirs(out_root, exist_ok=True)
    result = {"centroid": list(X), "test_views": sorted(test_names),
              "occlusion_px_source": "ticket-03 face_survey (jawlike rule, cited not re-derived)",
              "views": {}}
    n_train_constrain = 0
    for name in names:
        _, qvec, tvec, _ = imgs[name]
        R = qvec_to_R(np.array(qvec))
        t = np.array(tvec)
        Pc = R @ X + t
        front = bool(Pc[2] > 0)
        u = float(fx * Pc[0] / Pc[2] + cx) if front else -1.0
        v = float(fy * Pc[1] / Pc[2] + cy) if front else -1.0
        in_frame = bool(front and 0 <= u < w and 0 <= v < h)
        mb = None
        in_mask = False
        if name in track:
            x0, y0, x1, y1 = track[name]["bbox"]
            mb = [c / NATIVE_OVER_SPARSE for c in (x0, y0, x1, y1)]
            in_mask = bool(in_frame and mb[0] <= u <= mb[2] and mb[1] <= v <= mb[3])
        is_test = name in test_names
        depth_file = f"{pgsr_root}/output/A31B_ctrl/train/ours_30000/renders_depth/{name.replace('.JPG', '.jpg')}"
        has_depth = os.path.isfile(depth_file)
        constrain = bool(in_mask and not is_test and has_depth)
        n_train_constrain += constrain
        result["views"][name] = {"train": not is_test, "front": front,
                                 "in_frame": in_frame, "u": round(u, 1),
                                 "v": round(v, 1), "in_mask_bbox": in_mask,
                                 "has_renders_depth": has_depth,
                                 "constrains_fusion": constrain,
                                 "occlusion_px_cited": OCCLUDE_PX.get(name)}
        print(f"{name}: train={not is_test} inmask={in_mask} "
              f"depth={has_depth} constrain={constrain}", flush=True)
    result["n_train_views_constraining_face"] = n_train_constrain
    print(f"TRAIN views constraining the face: {n_train_constrain}/28", flush=True)

    # --- JET depth crops at the projected centroid (train face views only) ---
    crops = []
    for name in FACE_VIEWS:
        e = result["views"][name]
        tag = name.replace(".JPG", "")
        if e["train"] and e["in_frame"]:
            img = Image.open(
                f"{pgsr_root}/output/A31B_ctrl/train/ours_30000/renders_depth/{tag}.jpg")
            W, H = img.size  # render resolution (may differ from s3200)
            su, sv = W / w, H / h
            cu, cv = int(e["u"] * su), int(e["v"] * sv)
            crop = img.crop((max(0, cu - CROP), max(0, cv - CROP),
                             min(W, cu + CROP), min(H, cv + CROP)))
            crop.save(f"{out_root}/depthcrop_{tag}.png")
            crops.append(tag)
            print(f"{tag}: depth crop at ({cu},{cv}) of {W}x{H}", flush=True)
        else:
            print(f"{tag}: NO depth crop (train={e['train']} "
                  f"in_frame={e['in_frame']})", flush=True)
    result["depth_crops"] = crops

    # --- coverage bar chart: all 33 views, train/test x constrains ---
    fig = plt.figure(figsize=(14, 5))
    ax = fig.add_subplot(111)
    xs = np.arange(len(names))
    col = [("red" if n in test_names else
            "green" if result["views"][n]["constrains_fusion"] else "grey")
           for n in names]
    ax.bar(xs, [1] * len(names), color=col)
    ax.set_xticks(xs)
    ax.set_xticklabels([n.replace("A31_", "").replace(".JPG", "") for n in names],
                       rotation=90, fontsize=7)
    ax.set_yticks([])
    ax.set_title("Per-view face constraint (green=train+in-mask, "
                 "grey=train but off-face, red=llffhold test — never fused)")
    fig.tight_layout()
    fig.savefig(f"{out_root}/coverage.png", dpi=120)
    plt.close(fig)

    json.dump(result, open(f"{out_root}/depthview.json", "w"), indent=1)
    print(f"wrote {out_root}/depthview.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
