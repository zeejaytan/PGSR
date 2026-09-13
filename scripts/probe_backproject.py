"""Back-project one view's rendered depth under both pose conventions.

WHY. The regs-off model renders sensible depths (median ~= orbit distance,
nothing piled at max -- see probe_depth_hist.py), yet the fused A mesh lands
~5 units from its own training points. Either render.py's fork invert
(pose -> inv(pose) before Open3D integrate) is right and something else moved
the mesh, or the invert itself is the displacement. This settles it without
fusing anything: back-project masked clay depths with C2W=inv(pose) [fork]
versus C2W=pose [pre-fix] and measure which cloud sits on the training points.

Usage (inside a GPU allocation holding the model):
    python scripts/probe_backproject.py -s <data> -m <model> -i images_rgba -r 1 \
        --iteration 30000 --view 0 --ply <input.ply>

Prints mean nearest-neighbour distance to the training cloud and the fraction
within 0.02 / 0.05 scene-units, for each convention. Small derived numbers only.
"""
import torch
import numpy as np
from argparse import ArgumentParser
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scene import Scene
from arguments import ModelParams, PipelineParams, get_combined_args
from gaussian_renderer import GaussianModel, render


def main():
    parser = ArgumentParser(description="Back-projection pose probe")
    model = ModelParams(parser, sentinel=True)
    pipeline = PipelineParams(parser)
    parser.add_argument("--iteration", default=30000, type=int)
    parser.add_argument("--view", default=0, type=int, help="train view index")
    parser.add_argument("--ply", required=True, help="COLMAP-frame reference points")
    parser.add_argument("--samples", default=5000, type=int)
    args = get_combined_args(parser)

    with torch.no_grad():
        gaussians = GaussianModel(args.sh_degree)
        scene = Scene(args, gaussians, load_iteration=args.iteration, shuffle=False)
        view = scene.getTrainCameras()[args.view]
        out = render(view, gaussians, pipeline.extract(args),
                     torch.tensor([0, 0, 0], dtype=torch.float32, device="cuda"))
        depth = out["plane_depth"].squeeze().detach().cpu().double().numpy()
        H, W = depth.shape
        print(f"view {view.image_name} {W}x{H} Fx {view.Fx:.1f} Fy {view.Fy:.1f}")

        mask = None
        if view.mask is not None:
            mask = (view.mask.squeeze().cpu().numpy() >= 0.5)
            print(f"mask keep {mask.mean():.4f}")
        else:
            mask = np.ones_like(depth, bool)
        keep = mask & (depth > 0) & (depth < 5.0)
        vs, us = np.nonzero(keep)
        print(f"kept {len(us)} clay pixels")
        rng = np.random.default_rng(0)
        sel = rng.choice(len(us), min(args.samples, len(us)), replace=False)
        us, vs = us[sel], vs[sel]
        d = depth[vs, us]
        x = (us - view.Cx) / view.Fx * d
        y = (vs - view.Cy) / view.Fy * d
        cam = np.stack([x, y, d, np.ones_like(d)], -1)

        pose = np.identity(4)
        pose[:3, :3] = np.asarray(view.R).transpose(-1, -2)
        pose[:3, 3] = np.asarray(view.T)

        from plyfile import PlyData
        ply = PlyData.read(args.ply)
        ref = np.stack([np.asarray(ply["vertex"][a]) for a in "xyz"], -1).astype(np.float64)
        ref_t = torch.from_numpy(ref).float().cuda()

        for label, c2w in [("fork C2W=inv(pose)", np.linalg.inv(pose)),
                           ("prefix C2W=pose", pose)]:
            world = (c2w @ cam.T).T[:, :3]
            q = torch.from_numpy(world).float().cuda()
            nn = []
            for a in range(0, len(q), 1000):
                nn.append(torch.cdist(q[a:a + 1000], ref_t).min(1).values)
            nn = torch.cat(nn).cpu().numpy()
            print(f"{label}: meanNN {nn.mean():.4f} "
                  f"frac<0.02 {np.mean(nn < 0.02):.3f} frac<0.05 {np.mean(nn < 0.05):.3f}")


if __name__ == "__main__":
    main()
