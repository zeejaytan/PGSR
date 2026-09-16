"""Probe the QGS holder env for the torch/NumPy 2 mismatch (holder 30633299).

pip installed numpy 2.0.2 over the yml's 1.26.4; torch 2.2.2 was compiled
against NumPy 1.x and warns `_ARRAY_API not found` at import. If
torch.from_numpy fails here, training will crash and numpy must be pinned
back to 1.26.4 (the yml's own pin) before any run.
"""
import numpy as np
import torch

print("numpy", np.__version__)
print("torch", torch.__version__, "torch-cuda", torch.version.cuda)
t = torch.from_numpy(np.ones((3,), dtype=np.float32))
print("from_numpy ok", t.tolist())
import open3d  # noqa: E402
print("open3d ok", open3d.__version__)
import diff_quadratic_rasterization  # noqa: E402
import simple_knn  # noqa: E402
print("rasterizer+knn ok")
print("cuda available", torch.cuda.is_available())
