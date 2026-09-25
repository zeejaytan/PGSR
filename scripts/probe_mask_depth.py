#!/usr/bin/env python3
"""Probe one QGS train view: mask coverage vs gated depth (R1 ticket 04).

Answers: does the fusion gate actually zero background depth, and what do the
 surviving depths look like? Saves a depth-viz PNG for the agent's eye.
Usage (QGS env, from QGS checkout):
    python probe_mask_depth.py --qgs_repo <dir> --model_dir <out> [--cam 0]
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
    ap.add_argument("--cam", type=int, default=0)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    sys.path.insert(0, args.qgs_repo)
    from gaussian_renderer import GaussianModel, render
    from scene import Scene
    from utils.system_utils import load_config
    from PIL import Image

    config = load_config(os.path.join(args.model_dir, "config.yaml"))
    gaussians = GaussianModel(config.gs_model)
    scene = Scene(config, gaussians, load_iteration=30000, shuffle=False)
    cams = scene.getTrainCameras()
    cam = cams[args.cam]
    print(f"camera {args.cam}: {cam.image_name} {cam.image_path}")

    with Image.open(cam.image_path) as im:
        print("bands:", im.getbands())
    mask = cam.get_mask.squeeze()
    print("mask shape:", tuple(mask.shape),
          "kept frac:", float((mask >= 0.5).float().mean()))

    extractor_needed = False
    from utils.mesh_utils import GaussianExtractor
    bg = [1, 1, 1] if config.dataset.white_background else [0, 0, 0]
    ext = GaussianExtractor(gaussians, render, config.pipeline,
                            config.optimizer, bg_color=bg)
    with torch.no_grad():
        pkg = ext.render(cam, gaussians)
    depth = pkg["surf_depth"].squeeze()
    print("depth shape:", tuple(depth.shape), "device:", depth.device)
    d = depth.float().cpu().numpy()
    print("depth percentiles:", np.percentile(d, [0, 1, 5, 50, 95, 99, 100])
          .round(3))
    gated = d.copy()
    m = mask.float().cpu().numpy()
    gated[m < 0.5] = 0
    print("valid frac after gate:", float((gated > 0).mean()))
    dv = gated[gated > 0]
    if len(dv):
        print("gated-depth percentiles:",
              np.percentile(dv, [0, 1, 5, 50, 95, 99, 100]).round(3))

    out = args.out or os.path.join(args.model_dir, "mask_depth_probe.png")
    vis = np.zeros((*d.shape, 3), dtype=np.uint8)
    if len(dv):
        lo, hi = np.percentile(dv, [1, 99])
        norm = np.clip((np.log10(np.maximum(d, 1e-6)) - np.log10(max(lo, 1e-6)))
                       / max(np.log10(hi) - np.log10(max(lo, 1e-6)), 1e-9),
                       0, 1)
        vis[..., 0] = (norm * 255).astype(np.uint8)
        vis[..., 1] = (norm * 255).astype(np.uint8)
        vis[m < 0.5] = (255, 0, 0)
    Image.fromarray(vis).save(out)
    print("saved", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
