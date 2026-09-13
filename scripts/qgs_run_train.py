#!/usr/bin/env python3
"""PGSR-side QGS training driver (R1 ticket 03).

Stock QGS `train.py __main__` ships with the `training()` call commented out
(eval-only), so this driver replicates the `__main__` preamble (config merge,
seeds) and invokes `training()` directly. No QGS fork change.

Usage (inside the QGS env, from the QGS checkout):
    python /path/to/qgs_run_train.py --qgs_repo <dir> --conf <case-yaml>
"""
from __future__ import annotations

import argparse
import os
import random
import sys

import numpy as np
import torch
from omegaconf import OmegaConf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qgs_repo", required=True)
    ap.add_argument("--conf", required=True)
    ap.add_argument("--test_iterations", nargs="+", type=int, default=[7000, 30000])
    ap.add_argument("--save_iterations", nargs="+", type=int, default=[7000, 30000])
    args = ap.parse_args()

    sys.path.insert(0, args.qgs_repo)
    from train import training  # noqa: E402
    from utils.general_utils import safe_state  # noqa: E402

    base = os.path.join(args.qgs_repo, "config", "base.yaml")
    config = OmegaConf.merge(OmegaConf.load(base), OmegaConf.load(args.conf))
    config.model_path = str(config.model_path).replace(" ", "").replace("\n", "")
    print("Optimizing " + config.model_path, flush=True)

    safe_state(False)
    random.seed(0)
    np.random.seed(0)
    torch.manual_seed(0)
    torch.cuda.set_device(torch.device("cuda:0"))

    training(config, args.test_iterations, args.save_iterations, [], None, -1)
    print("\nTraining complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
