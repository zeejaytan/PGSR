#!/usr/bin/env python3
"""Locate the A31 sherd in 3D and render matching sherd-scale close-ups (ticket 04, phase 1).

Method (one method, both arms): back-project the A31-component bbox centres
(mask-derived, lama_trial/ticket03/face_survey/track_true.json) from the 7
face-visible views (A31_1114-1120, eye survey 2026-10-13) through the shared
33-camera sparse model, least-squares ray intersection -> ONE 3D centroid in
scene units. Both arms share bit-identical sparse geometry (md5-checked), so
the centroid is computed once and applied to both meshes.

Box: 2.5x the triangulated face width, clamped to [0.4, 1.0] scene units.

Renders per arm (identical centroid, box, viewpoints): 2 close-ups +
1 context view with the crop box marked. Matplotlib Agg, CPU-only.

Scale: MM_PER_UNIT=373.733 is the PROVISIONAL A03 scale (unproven for A31);
every mm axis/bar is labelled provisional. No scoring, no verdicts here.

Usage (from the repo checkout):
    python scripts/locate_a31_render_04.py <out_root> [mesh_file] [box|auto] [style]
Defaults: mesh_file=tsdf_fusion_post.ply, box=auto (from the sparse blob
extent around X, clamped to [0.10, 0.25] units), style=trisurf (shaded
surface; style=scatter draws z-coloured points instead).
Refuses loudly (nonzero exit, no renders) if the rays do not converge.
"""
from __future__ import annotations

import json
import os
import struct
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

MM_PER_UNIT = 373.733  # PROVISIONAL A03 scale; unproven for A31
NATIVE_OVER_SPARSE = 5568.0 / 3200.0  # track bboxes are native 5568x3712
FACE_VIEWS = [f"A31_{n}.JPG" for n in (1114, 1115, 1116, 1117, 1118, 1119, 1120)]
VIEWS_3D = [(30, -60), (10, 30)]
RESID_FAIL_PX = 25.0  # mean reprojection residual above this => NOT located
BAR_MM = 50.0  # provisional-mm scale bar drawn on close-ups


def read_cameras(path: str):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        cams = {}
        for _ in range(n):
            cam_id, model_id, w, h = struct.unpack("<IIQQ", fh.read(24))
            n_params = {0: 3, 1: 4, 2: 5, 3: 4, 4: 8, 5: 8, 6: 12, 7: 5,
                        8: 4, 9: 5, 10: 12}[model_id]
            params = struct.unpack("<" + "d" * n_params, fh.read(8 * n_params))
            cams[cam_id] = (model_id, w, h, params)
    return cams


def read_images(path: str):
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


def read_points3D(path: str):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        pts = np.empty((n, 3))
        for i in range(n):
            fh.read(8)
            pts[i] = struct.unpack("<3d", fh.read(24))
            fh.read(3)
            fh.read(8)
            trlen = struct.unpack("<Q", fh.read(8))[0]
            fh.read(trlen * 8)
    return pts


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
    if len(sys.argv) not in (2, 3, 4, 5):
        print("usage: locate_a31_render_04.py <out_root> [mesh_file] [box|auto] [style]",
              file=sys.stderr)
        return 1
    out_root = sys.argv[1]
    mesh_file = sys.argv[2] if len(sys.argv) > 2 else "tsdf_fusion_post.ply"
    box_arg = sys.argv[3] if len(sys.argv) > 3 else "auto"
    style = sys.argv[4] if len(sys.argv) > 4 else "trisurf"
    if style not in ("trisurf", "scatter"):
        print(f"unknown style {style}", file=sys.stderr)
        return 1
    pgsr_root = os.environ.get("PGSR_ROOT", "/data/gpfs/projects/punim2657/PGSR")

    track = json.load(open(f"{pgsr_root}/lama_trial/ticket03/face_survey/track_true.json"))
    sparse_dir = f"{pgsr_root}/data/17062025/A31_control/sparse"
    cams = read_cameras(f"{sparse_dir}/cameras.bin")
    imgs = read_images(f"{sparse_dir}/images.bin")
    model_id, w, h, params = cams[1]
    assert (model_id, w, h) == (1, 3200, 2133), f"unexpected camera {(model_id, w, h)}"
    fx, fy, cx, cy = params
    Kinv = np.array([[1 / fx, 0, -cx / fx], [0, 1 / fy, -cy / fy], [0, 0, 1]])
    print(f"camera: PINHOLE {w}x{h} fx={fx:.2f} fy={fy:.2f} cx={cx} cy={cy}", flush=True)
    print(f"sparse images: {len(imgs)}; first names: {sorted(imgs)[:2]}", flush=True)

    # --- triangulate: one ray per face-visible view ---
    centres, dirs, resid_info = [], [], {}
    for name in FACE_VIEWS:
        if name not in imgs:
            print(f"TRACK VIEW {name} MISSING FROM SPARSE -- ABORT", file=sys.stderr)
            return 2
        qvec, tvec, _ = imgs[name]
        R = qvec_to_R(np.array(qvec))
        t = np.array(tvec)
        C = -R.T @ t
        x0, y0, x1, y1 = track[name]["bbox"]
        u = ((x0 + x1) / 2) / NATIVE_OVER_SPARSE
        v = ((y0 + y1) / 2) / NATIVE_OVER_SPARSE
        d = R.T @ (Kinv @ np.array([u, v, 1.0]))
        d = d / np.linalg.norm(d)
        centres.append(C)
        dirs.append(d)
        resid_info[name] = {"u_s3200": round(u, 1), "v_s3200": round(v, 1)}
    C = np.array(centres)
    D = np.array(dirs)
    A = np.zeros((3, 3))
    b = np.zeros(3)
    for c, d in zip(C, D):
        P = np.eye(3) - np.outer(d, d)
        A += P
        b += P @ c
    X = np.linalg.solve(A, b)

    # reprojection residuals
    resids = []
    for name, c, d in zip(FACE_VIEWS, C, D):
        qvec, tvec, _ = imgs[name]
        R = qvec_to_R(np.array(qvec))
        t = np.array(tvec)
        p = R @ X + t
        uh, vh = fx * p[0] / p[2] + cx, fy * p[1] / p[2] + cy
        r = float(np.hypot(uh - resid_info[name]["u_s3200"], vh - resid_info[name]["v_s3200"]))
        resids.append(r)
        resid_info[name]["reproj_px"] = round(r, 1)
    mean_resid = float(np.mean(resids))
    print(f"centroid scene units: [{X[0]:.4f}, {X[1]:.4f}, {X[2]:.4f}]", flush=True)
    print(f"centroid provisional mm: [{X[0]*MM_PER_UNIT:.1f}, {X[1]*MM_PER_UNIT:.1f}, "
          f"{X[2]*MM_PER_UNIT:.1f}]", flush=True)
    print(f"reproj residuals px s3200: {[round(r,1) for r in resids]} mean={mean_resid:.1f}",
          flush=True)
    if mean_resid > RESID_FAIL_PX:
        print(f"RAYS DO NOT CONVERGE (mean {mean_resid:.1f}px > {RESID_FAIL_PX}px) -- "
              "SHERD NOT LOCATED, no renders", file=sys.stderr)
        return 3

    # --- box from triangulated face width (view 1117 = max occlusion) ---
    qvec, tvec, _ = imgs["A31_1117.JPG"]
    R = qvec_to_R(np.array(qvec))
    depth = float((R @ X + np.array(tvec))[2])
    x0, y0, x1, y1 = track["A31_1117.JPG"]["bbox"]
    face_w_units = ((x1 - x0) / NATIVE_OVER_SPARSE) * depth / fx
    if box_arg == "auto":
        # box from the sparse blob extent: p5-p95 spread per axis of sparse
        # points within 0.3 units of X, x1.2 cover, clamped to [0.10, 0.25]
        pts = read_points3D(f"{sparse_dir}/points3D.bin")
        near = pts[np.linalg.norm(pts - X, axis=1) < 0.3]
        q5 = np.quantile(near, 0.05, axis=0)
        q95 = np.quantile(near, 0.95, axis=0)
        spread = q95 - q5
        box = float(np.clip(np.ceil(float(spread.max() * 1.2) * 100) / 100, 0.10, 0.25))
        print(f"sparse blob near X: n={len(near)} p5={q5.round(3)} p95={q95.round(3)} "
              f"spread={spread.round(3)}", flush=True)
    else:
        box = float(box_arg)
    print(f"face width ~{face_w_units:.3f} units (~{face_w_units*MM_PER_UNIT:.0f}mm provisional); "
          f"box={box:.3f} units (~{box*MM_PER_UNIT:.0f}mm provisional)", flush=True)
    bar_mm = 20.0 if box * MM_PER_UNIT < 100 else BAR_MM

    import trimesh

    result = {
        "method": "back-project A31-component bbox centres (mask-derived, track_true.json) "
                  "from 7 face-visible views (A31_1114-1120) through the shared 33-camera "
                  "sparse model; least-squares ray intersection",
        "views": FACE_VIEWS,
        "centroid_scene_units": [round(float(v), 4) for v in X],
        "centroid_provisional_mm": [round(float(v * MM_PER_UNIT), 1) for v in X],
        "scale_note": "mm PROVISIONAL (A03 373.733 mm/unit, unproven for A31)",
        "per_view": resid_info,
        "mean_reproj_px_s3200": round(mean_resid, 1),
        "box_scene_units": round(box, 3),
        "box_provisional_mm": round(box * MM_PER_UNIT, 0),
        "box_source": box_arg,
        "render_style": style,
    }

    for arm, model in (("A_lama", "A31A_lama"), ("B_ctrl", "A31B_ctrl")):
        mesh_path = f"{pgsr_root}/output/{model}/mesh/{mesh_file}"
        outdir = f"{out_root}/{arm}"
        os.makedirs(outdir, exist_ok=True)
        m = trimesh.load(mesh_path, process=False)
        v = np.asarray(m.vertices, dtype=np.float64)
        f = np.asarray(m.faces, dtype=np.int64)
        print(f"{arm}: mesh verts={len(v)} bounds_min={v.min(0).round(3)} "
              f"bounds_max={v.max(0).round(3)}", flush=True)
        half = box / 2
        inside = np.all(np.abs(v - X) < half, axis=1)
        kept = np.flatnonzero(inside)
        lut = np.full(len(v), -1)
        lut[kept] = np.arange(len(kept))
        fmask = np.all(np.isin(f, kept), axis=1)
        n_in = int(inside.sum())
        result[f"{arm}_verts_in_box"] = n_in
        print(f"{arm}: verts in box={n_in} faces in box={int(fmask.sum())}", flush=True)
        vm = (v - X) * MM_PER_UNIT  # close-up coords: provisional mm about centroid
        if n_in > 50 and fmask.sum() > 0:
            sub = trimesh.Trimesh(vertices=vm[kept], faces=lut[f[fmask]], process=False)
        else:
            sub = None
            print(f"{arm}: BOX NEARLY EMPTY -- close-ups will show context only", flush=True)
        for k, (el, az) in enumerate(VIEWS_3D):
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection="3d")
            if sub is not None:
                if style == "trisurf":
                    ax.plot_trisurf(sub.vertices[:, 0], sub.vertices[:, 1], sub.vertices[:, 2],
                                    triangles=sub.faces, shade=True, linewidth=0,
                                    antialiased=False)
                else:
                    # z-coloured points (fragmented raw fusion reads as confetti
                    # under shaded triangles; points show the structure)
                    ax.scatter(sub.vertices[::2, 0], sub.vertices[::2, 1],
                               sub.vertices[::2, 2], s=2,
                               c=sub.vertices[::2, 2], cmap="coolwarm")
            # provisional-mm scale bar along x at the low corner
            if sub is not None:
                lo = sub.vertices.min(0)
                ax.plot([lo[0], lo[0] + bar_mm], [lo[1], lo[1]], [lo[2], lo[2]],
                        color="r", lw=3)
                ax.text(lo[0], lo[1], lo[2], f"{bar_mm:.0f} mm (provisional scale)",
                        color="r", fontsize=10)
            ax.view_init(elev=el, azim=az)
            ax.set_box_aspect((1, 1, 1))
            ax.set_xlabel("mm (provisional)")
            ax.set_ylabel("mm (provisional)")
            ax.set_title(f"{arm} A31 close-up, box ~{box*MM_PER_UNIT:.0f}mm (provisional) "
                         f"el={el} az={az}")
            fig.tight_layout()
            fig.savefig(f"{outdir}/closeup_{k}.png", dpi=110)
            plt.close(fig)
        # context: full footprint (provisional mm) with crop box
        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(111)
        ax.scatter(v[::5, 0] * MM_PER_UNIT, v[::5, 1] * MM_PER_UNIT, s=0.3)
        cxmm, cymm = X[0] * MM_PER_UNIT, X[1] * MM_PER_UNIT
        halfmm = box * MM_PER_UNIT / 2
        ax.add_patch(plt.Rectangle((cxmm - halfmm, cymm - halfmm),
                                   2 * halfmm, 2 * halfmm,
                                   fill=False, edgecolor="r", lw=1.5))
        ax.set_aspect("equal")
        ax.set_xlabel("mm (provisional)")
        ax.set_ylabel("mm (provisional)")
        ax.set_title(f"{arm} context: full footprint (mm, provisional), red box = A31 crop")
        fig.tight_layout()
        fig.savefig(f"{outdir}/context.png", dpi=110)
        plt.close(fig)
        print(f"{arm}: wrote closeup_0/1.png context.png", flush=True)

    with open(f"{out_root}/locate.json", "w") as fh:
        json.dump(result, fh, indent=1)
    print(f"wrote {out_root}/locate.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
