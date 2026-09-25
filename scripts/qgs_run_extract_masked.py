#!/usr/bin/env python3
"""PGSR-side QGS *masked* extraction driver (R1 ticket 04 audit recovery).

Why this exists: the pinned QGS repo never assigns `Camera.gt_alpha_mask`
outside its `None` default, so `render.py`'s fusion ran fully unmasked even
with `dataset.use_alpha: true` (ticket-01 NATIVE GO refuted 2026-09-21). This
driver mirrors `render.py`'s mesh section exactly, except it ports the alpha
construction: every train camera gets `gt_alpha_mask` from its own `get_mask`
(the RGBA 4th band QGS reads when `use_alpha` is set) BEFORE `reconstruction()`
fills the depth maps, so `extract_mesh_bounded()`'s existing
`depth[mask < 0.5] = 0` gate finally has something to gate on.

No QGS fork change: the QGS checkout stays at pin; only PGSR-side files run.
Same precedent as `scripts/qgs_run_train.py`.

Usage (inside the QGS env, from the QGS checkout):
    python /path/to/qgs_run_extract_masked.py --qgs_repo <dir> --model_dir <out>
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import open3d as o3d
import torch

# Pinned M8-parity extraction values (must match the run config AND R1).
VOXEL = 0.002
SDF_TRUNC = 0.01
DEPTH_TRUNC = 5.0
CLUSTER_KEEP = 10  # render.py hardcodes 10, ignoring config num_cluster (== 10)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qgs_repo", required=True)
    ap.add_argument("--model_dir", required=True,
                    help="QGS output dir holding config.yaml + point_cloud/")
    ap.add_argument("--iteration", type=int, default=30000)
    ap.add_argument("--out_name", default="fuse_masked.ply")
    args = ap.parse_args()

    sys.path.insert(0, args.qgs_repo)
    from gaussian_renderer import GaussianModel, render  # noqa: E402
    from scene import Scene  # noqa: E402
    from utils.mesh_utils import (GaussianExtractor,  # noqa: E402
                                  post_process_mesh)
    from utils.system_utils import load_config  # noqa: E402
    from PIL import Image  # noqa: E402

    config = load_config(os.path.join(args.model_dir, "config.yaml"))
    pipe = config.pipeline
    for key, want in (("voxel_size", VOXEL), ("sdf_trunc", SDF_TRUNC),
                      ("depth_trunc", DEPTH_TRUNC)):
        have = float(pipe[key])
        if abs(have - want) > 1e-12:
            print(f"config {key}={have}, want {want} -- refusing",
                  file=sys.stderr)
            return 1
    print(f"parity ok: voxel {VOXEL}, sdf {SDF_TRUNC}, depth {DEPTH_TRUNC}")

    gaussians = GaussianModel(config.gs_model)
    scene = Scene(config, gaussians, load_iteration=args.iteration,
                  shuffle=False)
    cams = scene.getTrainCameras()
    print(f"loaded iter {scene.loaded_iter}, {len(cams)} train cameras")

    # PORT: wire each camera's own alpha reader into the fusion gate. Refuse
    # loudly instead of fusing silently unmasked (the 2026-09-21 failure).
    fg_fracs = []
    for cam in cams:
        with Image.open(cam.image_path) as im:
            if len(im.getbands()) != 4:
                print(f"{cam.image_name}: bands {im.getbands()}, want RGBA"
                      " -- refusing", file=sys.stderr)
                return 1
        mask = cam.get_mask
        if mask is None:
            print(f"{cam.image_name}: get_mask None -- refusing",
                  file=sys.stderr)
            return 1
        fg_fracs.append(float((mask >= 0.5).float().mean()))
        # Squeeze the leading singleton dim: the upstream gate
        # (`depth[(mask < 0.5)] = 0`) boolean-indexes a 2-D depth map, which a
        # (1, H, W) mask cannot index (IndexError — this path never ran
        # upstream). Squeezed (H, W) gates the right pixels.
        cam.gt_alpha_mask = mask.squeeze()
    fg = float(np.mean(fg_fracs))
    print(f"masks wired on {len(cams)} cameras, mean foreground {fg:.4f} "
          f"(min {min(fg_fracs):.4f}, max {max(fg_fracs):.4f})")
    if not 0.001 < fg < 0.5:
        print(f"foreground fraction {fg:.4f} outside (0.001, 0.5): masks look "
              "inverted or broken -- refusing", file=sys.stderr)
        return 1

    bg = [1, 1, 1] if config.dataset.white_background else [0, 0, 0]
    extractor = GaussianExtractor(gaussians, render, pipe, config.optimizer,
                                  bg_color=bg)
    extractor.reconstruction(cams)

    # Shape guard: a mask that doesn't match its depth map would gate the
    # wrong pixels. Compare squeezed shapes (masks carry a leading singleton
    # dim). Refuse instead of fusing garbage.
    for i, cam in enumerate(cams):
        mshape = tuple(cam.gt_alpha_mask.squeeze().shape)
        dshape = tuple(extractor.depthmaps[i].squeeze().shape)
        if mshape != dshape:
            print(f"camera {i}: mask {mshape} vs depth {dshape} -- refusing",
                  file=sys.stderr)
            return 1
    print("mask/depth shapes agree")

    train_dir = os.path.join(args.model_dir, "train",
                             f"ours_{scene.loaded_iter}")
    os.makedirs(train_dir, exist_ok=True)
    out = os.path.join(train_dir, args.out_name)
    if os.path.exists(out):
        print(f"{out} exists -- refusing (no overwrite).", file=sys.stderr)
        return 1

    mesh = extractor.extract_mesh_bounded(voxel_size=VOXEL, sdf_trunc=SDF_TRUNC,
                                          depth_trunc=DEPTH_TRUNC)
    o3d.io.write_triangle_mesh(out, mesh)
    print(f"masked mesh saved at {out}")
    mesh_post = post_process_mesh(mesh, cluster_to_keep=CLUSTER_KEEP)
    post = out.replace(".ply", "_post.ply")
    o3d.io.write_triangle_mesh(post, mesh_post)
    print(f"masked post mesh saved at {post}")
    print(f"verts raw {len(mesh.vertices)}, post {len(mesh_post.vertices)}")
    bounds = np.asarray(mesh_post.get_axis_aligned_bounding_box()
                         .get_box_points())
    print(f"post bounds min {bounds.min(0).round(3)} "
          f"max {bounds.max(0).round(3)} (scene units)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
