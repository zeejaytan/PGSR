#!/usr/bin/env python3
"""Cross-view depth disagreement for the QGS 30k model (R1 ticket 04).

For sampled train-view pairs (nearest neighbours by camera centre):
backproject view A's masked valid depths to world, reproject into view B,
and compare predicted z against view B's own rendered depth at the pixels
where BOTH views hold valid masked depth. Reports disagreement in mm
(373.733 sidecar). Large values = the splat model is view-inconsistent
(floaters), which fuses into curtains; small values = integration at fault.
Usage (QGS env, from QGS checkout):
    python probe_depth_disagree_qgs.py --qgs_repo <dir> --model_dir <out>
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import torch

MM = 373.73332518281325


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qgs_repo", required=True)
    ap.add_argument("--model_dir", required=True)
    ap.add_argument("--pairs", type=int, default=12)
    args = ap.parse_args()

    sys.path.insert(0, args.qgs_repo)
    from gaussian_renderer import GaussianModel, render
    from scene import Scene
    from utils.mesh_utils import GaussianExtractor
    from utils.system_utils import load_config

    config = load_config(os.path.join(args.model_dir, "config.yaml"))
    gaussians = GaussianModel(config.gs_model)
    scene = Scene(config, gaussians, load_iteration=30000, shuffle=False)
    cams = scene.getTrainCameras()

    bg = [1, 1, 1] if config.dataset.white_background else [0, 0, 0]
    ext = GaussianExtractor(gaussians, render, config.pipeline,
                            config.optimizer, bg_color=bg)

    # Nearest-neighbour pairs by camera translation direction.
    def _t(cam):
        return as_np(cam.world_view_transform)[3, :3]

    centers = np.stack([_t(cam) for cam in cams])
    centers = centers / (np.linalg.norm(centers, axis=1, keepdims=True) + 1e-9)
    idx = np.linspace(0, len(cams) - 1, args.pairs).astype(int)
    pairs = []
    for i in idx:
        d = np.linalg.norm(centers - centers[i], axis=1)
        d[i] = np.inf
        pairs.append((int(i), int(np.argmin(d))))

    def render_depth_mask(cam):
        with torch.no_grad():
            pkg = ext.render(cam, gaussians)
        depth = pkg["surf_depth"].squeeze().float().cpu().numpy()
        mask = cam.get_mask.squeeze().float().cpu().numpy()
        return depth, mask

    def as_np(x):
        if torch.is_tensor(x):
            return x.detach().cpu().numpy()
        return np.asarray(x)

    def cam_mats(cam):
        E = as_np(cam.world_view_transform)  # noqa: F841 (kept for clarity)
        return E

    all_abs = []
    for (ia, ib) in pairs:
        da, ma = render_depth_mask(cams[ia])
        db, mb = render_depth_mask(cams[ib])
        Ea = as_np(cams[ia].world_view_transform)
        Eb = as_np(cams[ib].world_view_transform)
        # 3DGS stores the transpose; un-transpose to plain W2C.
        if Ea.shape == (4, 4):
            Ea = Ea.T
            Eb = Eb.T
        Ka = as_np(cams[ia].cam_intr).astype(float)
        Kb = as_np(cams[ib].cam_intr).astype(float)
        ys, xs = np.nonzero((ma >= 0.5) & (da > 0))
        d = da[ys, xs]
        xa = (xs - Ka[2]) * d / Ka[0]
        ya = (ys - Ka[3]) * d / Ka[1]
        pts = np.stack([xa, ya, d, np.ones_like(d)])
        world = (np.linalg.inv(Ea) @ pts)[:3]
        pb = (Eb @ np.vstack([world, np.ones((1, world.shape[1]))]))[:3]
        zb = pb[2]
        ub = (pb[0] / np.maximum(zb, 1e-9) * Kb[0] + Kb[2]).round().astype(int)
        vb = (pb[1] / np.maximum(zb, 1e-9) * Kb[1] + Kb[3]).round().astype(int)
        H, W = db.shape
        inside = (ub >= 0) & (ub < W) & (vb >= 0) & (vb < H) & (zb > 0)
        ub, vb, zb = ub[inside], vb[inside], zb[inside]
        both = (mb[vb, ub] >= 0.5) & (db[vb, ub] > 0)
        if both.sum() < 100:
            print(f"pair {ia}->{ib}: only {both.sum()} shared px, skip")
            continue
        dis = np.abs(zb[both] - db[vb[both], ub[both]]) * MM
        all_abs.append(dis)
        print(f"pair {ia}->{ib}: n={both.sum()} "
              f"p50={np.median(dis):.2f}mm mean={dis.mean():.2f}mm "
              f"p90={np.percentile(dis, 90):.2f}mm")
    if all_abs:
        all_abs = np.concatenate(all_abs)
        print(f"ALL: n={len(all_abs)} p50={np.median(all_abs):.2f}mm "
              f"mean={all_abs.mean():.2f}mm p90={np.percentile(all_abs, 90):.2f}mm")
    else:
        print("no usable pairs -- refusing")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
