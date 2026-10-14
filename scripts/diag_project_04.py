"""2b-prime: project raw-box verts through training-view COLMAP cameras onto photos.

Reads centroid+box from work/edge_04b/locate.json (phase 2a, shared geometry),
projects each arm's raw-mesh box verts through the SHARED 33-camera sparse model
(data/17062025/A31_control/sparse) onto that arm's own photo, and writes
verts-on-photo overlays + inside-photo / inside-mask fractions.

Usage: diag_project_04.py <out_root>
"""
import json
import os
import struct
import sys

import numpy as np
import trimesh
from PIL import Image, ImageDraw

NATIVE_OVER_SPARSE = 5568.0 / 3200.0  # track bboxes are native 5568x3712
VIEWS = ["A31_1116.JPG", "A31_1117.JPG"]
ARMS = (("A_lama", "A31A_lama", "A31_lama"), ("B_ctrl", "A31B_ctrl", "A31_control"))
OVERLAY_SCALE = 0.4  # 3200x2133 -> 1280x853 panels


def read_cameras(path):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        out = {}
        for _ in range(n):
            cid = struct.unpack("<i", fh.read(4))[0]
            model = struct.unpack("<i", fh.read(4))[0]
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
            iid = struct.unpack("<I", fh.read(4))[0]
            qvec = struct.unpack("<4d", fh.read(32))
            tvec = struct.unpack("<3d", fh.read(24))
            cam = struct.unpack("<I", fh.read(4))[0]
            name = b""
            while True:
                ch = fh.read(1)
                if ch == b"\x00":
                    break
                name += ch
            name = name.decode()
            n2 = struct.unpack("<Q", fh.read(8))[0]
            fh.read(n2 * 24)
            imgs[name] = (qvec, tvec, cam)
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
        print("usage: diag_project_04.py <out_root>", file=sys.stderr)
        return 1
    out_root = sys.argv[1]
    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")

    prev = json.load(open(f"{pgsr_root}/work/edge_04b/locate.json"))
    X = np.array(prev["centroid_scene_units"])
    box = float(prev["box_scene_units"])
    half = box / 2
    track = json.load(open(f"{pgsr_root}/lama_trial/ticket03/face_survey/track_true.json"))

    sparse_dir = f"{pgsr_root}/data/17062025/A31_control/sparse"
    cams = read_cameras(f"{sparse_dir}/cameras.bin")
    imgs = read_images(f"{sparse_dir}/images.bin")
    model_id, w, h, params = cams[1]
    assert (model_id, w, h) == (1, 3200, 2133), f"unexpected camera {(model_id, w, h)}"
    fx, fy, cx, cy = params

    os.makedirs(out_root, exist_ok=True)
    result = {"views": {}, "box_scene_units": box,
              "centroid_scene_units": [round(float(v), 4) for v in X]}

    for view in VIEWS:
        if view not in imgs:
            print(f"VIEW {view} MISSING FROM SPARSE -- ABORT", file=sys.stderr)
            return 2
        x0, y0, x1, y1 = track[view]["bbox"]
        # mask bbox from 5568-frame into the 3200-frame of camera and photos
        mb = [c / NATIVE_OVER_SPARSE for c in (x0, y0, x1, y1)]
        qvec, tvec, _ = imgs[view]
        R = qvec_to_R(np.array(qvec))
        t = np.array(tvec)
        panels = []
        vres = {}
        for arm, model, photodir in ARMS:
            mesh = trimesh.load(f"{pgsr_root}/output/{model}/mesh/tsdf_fusion.ply",
                                process=False)
            v = np.asarray(mesh.vertices)
            inside = v[np.all(np.abs(v - X) < half, axis=1)]
            Pc = (R @ inside.T).T + t
            front = Pc[:, 2] > 0
            u = fx * Pc[:, 0] / np.where(front, Pc[:, 2], 1) + cx
            vv = fy * Pc[:, 1] / np.where(front, Pc[:, 2], 1) + cy
            in_img = front & (u >= 0) & (u < w) & (vv >= 0) & (vv < h)
            in_mask = in_img & (u >= mb[0]) & (u <= mb[2]) & (vv >= mb[1]) & (vv <= mb[3])
            n = len(inside)
            vres[arm] = {"n_box_verts": n,
                         "frac_in_photo": round(float(in_img.sum()) / n, 4),
                         "frac_in_mask": round(float(in_mask.sum()) / n, 4)}
            print(f"{view} {arm}: n={n} in_photo={in_img.sum()} "
                  f"({vres[arm]['frac_in_photo']:.3f}) in_mask={in_mask.sum()} "
                  f"({vres[arm]['frac_in_mask']:.3f})", flush=True)

            photo = Image.open(
                f"{pgsr_root}/data/17062025/{photodir}/images/{view}").convert("RGB")
            assert photo.size == (w, h), f"unexpected photo size {photo.size}"
            panel = photo.resize((int(w * OVERLAY_SCALE), int(h * OVERLAY_SCALE)))
            d = ImageDraw.Draw(panel)
            s = OVERLAY_SCALE
            d.rectangle([mb[0] * s, mb[1] * s, mb[2] * s, mb[3] * s],
                        outline=(255, 0, 0), width=3)
            uu, vvv = u[in_img] * s, vv[in_img] * s
            step = max(1, len(uu) // 3000)
            for px, py in zip(uu[::step], vvv[::step]):
                d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(0, 255, 255))
            Xc = R @ X + t
            if Xc[2] > 0:
                px, py = (fx * Xc[0] / Xc[2] + cx) * s, (fy * Xc[1] / Xc[2] + cy) * s
                d.line([px - 15, py, px + 15, py], fill=(255, 255, 0), width=3)
                d.line([px, py - 15, px, py + 15], fill=(255, 255, 0), width=3)
            d.text((10, 10), f"{arm} {view}: box verts cyan, mask bbox red, "
                             f"centroid yellow ({vres[arm]['frac_in_mask'] * 100:.1f}% "
                             f"of {n} in mask)", fill=(255, 255, 0))
            panel.save(f"{out_root}/{arm}_{view.replace('.JPG', '')}_overlay.png")
            panels.append(panel)
            del mesh, v, inside, Pc

        both = Image.new("RGB", (panels[0].width * 2 + 10, panels[0].height))
        both.paste(panels[0], (0, 0))
        both.paste(panels[1], (panels[0].width + 10, 0))
        both.save(f"{out_root}/sidebyside_{view.replace('.JPG', '')}.png")
        print(f"{view}: wrote overlays + side-by-side", flush=True)
        result["views"][view] = {"mask_bbox_s3200": [round(c, 1) for c in mb],
                                 "arms": vres}

    json.dump(result, open(f"{out_root}/project.json", "w"), indent=1)
    print(f"wrote {out_root}/project.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
