#!/usr/bin/env python3
"""Patch deviation for ticket 02: compare LaMa-filled patch vs held-out truth.

Compares the filled held-out patch (gate02/out) against the original photo
(gate02/A31_1116.JPG) inside the patch box from gate02/patch.json, and writes
1:1 close-ups plus stats. Separation of concerns vs measure_edge_baseline.py:
that script scores a FUSED MESH in mm (plane-fit RMS via MM_PER_UNIT); this one
scores 2D PHOTO pixels before any training exists, in gray levels AND in mm via
patch.json mm_per_px (pinhole back-projection at the patch sparse-median depth).

Usage:
    python scripts/measure_patch_deviation.py <gate02_dir> <artifacts_out_dir>
Writes: stats.json, side_by_side.png, true_1to1.png, fill_1to1.png printed on stdout.
Refuses loudly on unread/mismatched inputs instead of printing partial numbers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: measure_patch_deviation.py <gate02_dir> <out_dir>", file=sys.stderr)
        return 1
    gate, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        from PIL import Image
    except ImportError as e:  # noqa: BLE001
        print(f"PIL import failed: {e}", file=sys.stderr)
        return 1

    try:
        p = json.loads((gate / "patch.json").read_text())
        true = np.array(Image.open(gate / "A31_1116.JPG").convert("RGB"))
        fill = np.array(Image.open(gate / "out" / "a31_1116_mask.png").convert("RGB"))
    except Exception as e:  # noqa: BLE001
        print(f"READ FAIL {e}"[:200], file=sys.stderr)
        return 1
    if true.shape != fill.shape:
        print(f"SHAPE MISMATCH true {true.shape} fill {fill.shape}", file=sys.stderr)
        return 1
    x0, y0, s = (p["patch"][k] for k in ("x0", "y0", "size"))
    H, W, _ = true.shape
    if not (0 <= x0 < x0 + s <= W and 0 <= y0 < y0 + s <= H):
        print(f"PATCH BOX OUT OF BOUNDS {x0},{y0},{s} vs {W}x{H}", file=sys.stderr)
        return 1
    mpp = float(p["mm_per_px"])
    px_side_mm = round(s * mpp, 2)

    bt = true[y0:y0 + s, x0:x0 + s].astype(np.float64).mean(-1)
    bf = fill[y0:y0 + s, x0:x0 + s].astype(np.float64).mean(-1)
    d = bf - bt
    ad = np.abs(d)
    stats = {
        "patch": {"cx": p["patch"]["cx"], "cy": p["patch"]["cy"], "size": s,
                  "x0": x0, "y0": y0},
        "mm_per_px": mpp, "patch_side_mm": px_side_mm,
        "gray": {"mean_abs": round(float(ad.mean()), 2),
                 "rms": round(float(np.sqrt((d ** 2).mean())), 2),
                 "p50_abs": round(float(np.quantile(ad, 0.5)), 2),
                 "p90_abs": round(float(np.quantile(ad, 0.9)), 2),
                 "max_abs": round(float(ad.max()), 2),
                 "bias": round(float(d.mean()), 2)},
        "mm_proxy": {"mean_abs": round(float(ad.mean() * mpp), 3),
                     "rms": round(float(np.sqrt((d ** 2).mean()) * mpp), 3),
                     "p90_abs": round(float(np.quantile(ad, 0.9) * mpp), 3),
                     "max_abs": round(float(ad.max() * mpp), 3)},
        "note": ("mm_proxy multiplies gray-level residuals by the pinhole "
                 "mm/px at patch depth; it is a PHOTO-domain proxy, NOT a "
                 "surface deviation. Ticket-02 PASS/MISS is decided on the "
                 "rendered close-ups + gray residuals, not on mm_proxy."),
    }
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "stats.json").write_text(json.dumps(stats, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pad = 120
    xa, xb = max(0, x0 - pad), min(W, x0 + s + pad)
    ya, yb = max(0, y0 - pad), min(H, y0 + s + pad)
    ctx_t, ctx_f = true[ya:yb, xa:xb], fill[ya:yb, xa:xb]
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    for a, im, t in ((ax[0], ctx_t, "true (held-out answer)"),
                     (ax[1], ctx_f, "LaMa fill (pinned big-lama)")):
        a.imshow(im)
        a.add_patch(plt.Rectangle((x0 - xa, y0 - ya), s, s, fill=False,
                                  edgecolor="lime", lw=2))
        a.set_title(f"{t}\nbox {s}px = {px_side_mm} mm side, {mpp} mm/px")
        a.axis("off")
    fig.tight_layout()
    fig.savefig(outdir / "side_by_side.png", dpi=110)
    plt.close(fig)

    for name, box in (("true_1to1.png", true[y0:y0 + s, x0:x0 + s]),
                      ("fill_1to1.png", fill[y0:y0 + s, x0:x0 + s])):
        fig = plt.figure(figsize=(6, 6))
        plt.imshow(box, interpolation="nearest")
        plt.title(f"{name.split('_')[0]} 1:1 ({s}px = {px_side_mm} mm)")
        plt.axis("off")
        fig.tight_layout()
        fig.savefig(outdir / name, dpi=110)
        plt.close(fig)

    print(json.dumps(stats))
    print(f"wrote {outdir}/stats.json side_by_side.png true_1to1.png fill_1to1.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
