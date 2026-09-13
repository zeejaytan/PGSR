"""Histogram rendered plane_depth for a few views of a trained PGSR model.

WHY. The regs-off A03_noreg model renders honest RGB (22.9 dB held out) but its
fusion-masked mesh lands ~5 units from its own training points, out at the
max-depth range. Two suspects: the fusion pose is still wrong, or the model's
plane_depth overshoots (unflattened Gaussians -- the flattening losses were the
thing switched off) and fusion parks the clay at max range. Piled-at-5.0
depths convict the depths; a sensible spread over the tray acquits them and
points at the pose.

Usage (inside a GPU allocation holding the model):
    python scripts/probe_depth_hist.py -s <data> -m <model> [-i images_rgba] [--iteration 30000] [--views 8]

CPU-only prints, no files written. Small derived numbers only.
"""
import torch
from argparse import ArgumentParser
from scene import Scene
from arguments import ModelParams, PipelineParams, get_combined_args
from gaussian_renderer import GaussianModel, render


def main():
    parser = ArgumentParser(description="Depth-histogram probe parameters")
    model = ModelParams(parser, sentinel=True)
    pipeline = PipelineParams(parser)
    parser.add_argument("--iteration", default=30000, type=int)
    parser.add_argument("--views", default=8, type=int,
                        help="evenly spread train views to probe")
    args = get_combined_args(parser)

    with torch.no_grad():
        gaussians = GaussianModel(args.sh_degree)
        scene = Scene(args, gaussians, load_iteration=args.iteration, shuffle=False)
        print(f"cameras_extent {scene.cameras_extent}")
        bg = torch.tensor([1, 1, 1] if args.white_background else [0, 0, 0],
                          dtype=torch.float32, device="cuda")
        train = scene.getTrainCameras()
        n = len(train)
        step = max(1, n // args.views)
        idxs = list(range(0, n, step))[:args.views]
        print(f"{n} train views, probing {len(idxs)}: {idxs}")
        pipe = pipeline.extract(args)
        for k in idxs:
            view = train[k]
            out = render(view, gaussians, pipe, bg)
            d = out["plane_depth"].squeeze().detach().cpu().flatten().float()
            h, w = out["plane_depth"].shape[-2:]
            valid = d[d > 0]
            f_zero = 1.0 - len(valid) / len(d)
            if len(valid):
                q = torch.quantile(valid, torch.tensor([0.0, 0.05, 0.5, 0.95, 1.0]))
                f_max = (valid >= 4.99).float().mean().item()
                print(f"{view.image_name} {w}x{h} "
                      f"min {q[0]:.3f} p5 {q[1]:.3f} med {q[2]:.3f} "
                      f"p95 {q[3]:.3f} max {q[4]:.3f} "
                      f"zero {f_zero:.3f} pile_at_max {f_max:.3f}")
            else:
                print(f"{view.image_name} {w}x{h} ALL ZERO")


if __name__ == "__main__":
    main()
