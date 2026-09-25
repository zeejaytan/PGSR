#!/usr/bin/env python3
"""Backproject QGS masked depths into world space (R1 ticket 04).

Decides between two suspects for the scene-spanning curtain in the fused
mesh: wrong camera geometry (points land smeared) vs TSDF integration
(points land on the sherds, volume at fault). Compares against the COLMAP
input points as the training-point reference.
Usage (QGS env, from QGS checkout):
    python probe_backproject_qgs.py --qgs_repo <dir> --model_dir <out>
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import torch


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qgs_repo", required=True)
    ap.add_argument("--model_dir", required=True)
    ap.add_argument("--cams", type=int, default=3)
    args = ap.parse_args()

    sys.path.insert(0, args.qgs_repo)
    from gaussian_renderer import GaussianModel, render
    from scene import Scene
    from utils.mesh_utils import GaussianExtractor, to_cam_open3d
    from utils.system_utils import load_config
    from plyfile import PlyData

    config = load_config(os.path.join(args.model_dir, "config.yaml"))
    gaussians = GaussianModel(config.gs_model)
    scene = Scene(config, gaussians, load_iteration=30000, shuffle=False)
    cams = scene.getTrainCameras()[:args.cams]

    ply = PlyData.read(os.path.join(args.model_dir, "input.ply"))
    v = ply["vertex"]
    pts = np.vstack([v["x"], v["y"], v["z"]]).T
    print("input points bounds min", pts.min(0).round(3),
          "max", pts.max(0).round(3))

    bg = [1, 1, 1] if config.dataset.white_background else [0, 0, 0]
    ext = GaussianExtractor(gaussians, render, config.pipeline,
                            config.optimizer, bg_color=bg)
    traj = to_cam_open3d(cams)
    allp = []
    with torch.no_grad():
        for i, cam in enumerate(cams):
            pkg = ext.render(cam, gaussians)
            depth = pkg["surf_depth"].squeeze().float().cpu().numpy()
            mask = cam.get_mask.squeeze().float().cpu().numpy()
            keep = (mask >= 0.5) & (depth > 0)
            ys, xs = np.nonzero(keep)
            print(f"cam {i}: kept {keep.sum()} px, "
                  f"depth range {depth[keep].min():.3f}..{depth[keep].max():.3f}")
            K = traj[i].intrinsic.intrinsic_matrix
            E = traj[i].extrinsic  # W2C
            C2W = np.linalg.inv(E)
            d = depth[keep]
            x = (xs - K[0, 2]) * d / K[0, 0]
            y = (ys - K[1, 2]) * d / K[1, 1]
            cam_pts = np.stack([x, y, d, np.ones_like(d)])
            world = (C2W @ cam_pts)[:3].T
            allp.append(world)
            print(f"cam {i}: world bounds min {world.min(0).round(3)} "
                  f"max {world.max(0).round(3)}")
    allp = np.vstack(allp)
    print("ALL backprojected bounds min", allp.min(0).round(3),
          "max", allp.max(0).round(3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
