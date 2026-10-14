"""2b-prime-2: mask-interior box verts only — trisurf free-orbit + photo projection.

For each arm x photo-view (A31_1116/1117): keep the raw-box verts projecting
INSIDE the track mask bbox, build their submesh, render shaded trisurf at the
same 2 orbit viewpoints as phase 2a, and re-project the kept verts onto the
photo. Reads centroid+box from work/edge_04b/locate.json (same rounded values
as 2b-prime, so counts match project.json).

Usage: diag_maskpatch_04.py <out_root>
"""
import json
import os
import struct
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

NATIVE_OVER_SPARSE = 5568.0 / 3200.0  # track bboxes are native 5568x3712
MM_PER_UNIT = 373.733  # PROVISIONAL (A03 scale, unproven for A31)
VIEWS = ["A31_1116.JPG", "A31_1117.JPG"]
ARMS = (("A_lama", "A31A_lama", "A31_lama"), ("B_ctrl", "A31B_ctrl", "A31_control"))
ORBITS = [(30, -60), (10, 30)]
OVERLAY_SCALE = 0.4


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
            fh.read(n2d * 24)  # x, y (double), point3D_id (int64)
            imgs[name.decode()] = (qvec, tvec, cam_id)
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
        print("usage: diag_maskpatch_04.py <out_root>", file=sys.stderr)
        return 1
    out_root = sys.argv[1]
    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")

    prev = json.load(open(f"{pgsr_root}/work/edge_04b/locate.json"))
    X = np.array(prev["centroid_scene_units"])
    box = float(prev["box_scene_units"])
    half = box / 2
    bar_mm = 20.0
    track = json.load(open(f"{pgsr_root}/lama_trial/ticket03/face_survey/track_true.json"))

    sparse_dir = f"{pgsr_root}/data/17062025/A31_control/sparse"
    cams = read_cameras(f"{sparse_dir}/cameras.bin")
    imgs = read_images(f"{sparse_dir}/images.bin")
    model_id, w, h, params = cams[1]
    assert (model_id, w, h) == (1, 3200, 2133), f"unexpected camera {(model_id, w, h)}"
    fx, fy, cx, cy = params

    os.makedirs(out_root, exist_ok=True)
    result = {"box_scene_units": box, "views": {}}

    for view in VIEWS:
        tag = view.replace(".JPG", "")
        x0, y0, x1, y1 = track[view]["bbox"]
        mb = [c / NATIVE_OVER_SPARSE for c in (x0, y0, x1, y1)]
        qvec, tvec, _ = imgs[view]
        R = qvec_to_R(np.array(qvec))
        t = np.array(tvec)
        vres = {}
        for arm, model, photodir in ARMS:
            mesh = trimesh.load(f"{pgsr_root}/output/{model}/mesh/tsdf_fusion.ply",
                                process=False)
            v = np.asarray(mesh.vertices)
            f = np.asarray(mesh.faces)
            box_idx = np.nonzero(np.all(np.abs(v - X) < half, axis=1))[0]
            inside = v[box_idx]
            Pc = (R @ inside.T).T + t
            front = Pc[:, 2] > 0
            u = fx * Pc[:, 0] / np.where(front, Pc[:, 2], 1) + cx
            vv = fy * Pc[:, 1] / np.where(front, Pc[:, 2], 1) + cy
            in_mask = (front & (u >= mb[0]) & (u <= mb[2])
                       & (vv >= mb[1]) & (vv <= mb[3]))
            kept = box_idx[in_mask]
            n_box, n_kept = len(box_idx), len(kept)
            lut = np.full(len(v), -1)
            lut[kept] = np.arange(n_kept)
            fmask = np.all(np.isin(f, kept), axis=1)
            n_faces = int(fmask.sum())
            vres[arm] = {"n_box_verts": n_box, "n_mask_interior_verts": n_kept,
                         "n_mask_interior_faces": n_faces}
            print(f"{tag} {arm}: box={n_box} mask_interior_verts={n_kept} "
                  f"faces={n_faces}", flush=True)

            # --- photo projection of kept verts ---
            photo = Image.open(
                f"{pgsr_root}/data/17062025/{photodir}/images/{view}").convert("RGB")
            panel = photo.resize((int(w * OVERLAY_SCALE), int(h * OVERLAY_SCALE)))
            d = ImageDraw.Draw(panel)
            s = OVERLAY_SCALE
            d.rectangle([mb[0] * s, mb[1] * s, mb[2] * s, mb[3] * s],
                        outline=(255, 0, 0), width=3)
            uk, vk = u[in_mask] * s, vv[in_mask] * s
            step = max(1, len(uk) // 3000)
            for px, py in zip(uk[::step], vk[::step]):
                d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(0, 255, 255))
            d.text((10, 10), f"{arm} {view}: MASK-INTERIOR verts only "
                             f"({n_kept}/{n_box}), mask bbox red", fill=(255, 255, 0))
            panel.save(f"{out_root}/{arm}_{tag}_maskproj.png")

            # --- shaded trisurf of kept submesh, same 2 orbits ---
            if n_kept > 50 and n_faces > 0:
                sub = trimesh.Trimesh(vertices=v[kept], faces=lut[f[fmask]],
                                      process=False)
                for k, (el, az) in enumerate(ORBITS):
                    fig = plt.figure(figsize=(8.8, 8.8))
                    ax = fig.add_subplot(111, projection="3d")
                    ax.plot_trisurf(sub.vertices[:, 0], sub.vertices[:, 1],
                                    sub.vertices[:, 2], triangles=sub.faces,
                                    shade=True, linewidth=0, antialiased=False)
                    ax.view_init(elev=el, azim=az)
                    ax.set_title(f"{arm} {tag}-mask-interior, "
                                 f"{n_kept}v/{n_faces}f, el={el} az={az}\n"
                                 f"(units x{MM_PER_UNIT:.1f}=provisional mm)")
                    lo = sub.vertices.min(0)
                    ax.plot([lo[0], lo[0] + bar_mm / MM_PER_UNIT],
                            [lo[1], lo[1]], [lo[2], lo[2]], color="r", lw=3)
                    ax.text(lo[0], lo[1], lo[2],
                            f"{bar_mm:.0f} mm (provisional scale)",
                            color="r", fontsize=10)
                    fig.savefig(f"{out_root}/{arm}_{tag}_tri_{k}.png", dpi=100)
                    plt.close(fig)
            else:
                print(f"{tag} {arm}: submesh too small, skipping trisurf", flush=True)
            del mesh, v, f, inside, Pc
        result["views"][view] = {"mask_bbox_s3200": [round(c, 1) for c in mb],
                                 "arms": vres}
        print(f"{tag}: done", flush=True)

    json.dump(result, open(f"{out_root}/maskpatch.json", "w"), indent=1)
    print(f"wrote {out_root}/maskpatch.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
