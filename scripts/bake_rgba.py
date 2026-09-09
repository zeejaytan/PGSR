#!/usr/bin/env python3
"""Bake sherd-only masks into RGBA alpha for PGSR fusion-time masking.

Reads undistorted RGB views plus full-size L masks, NEAREST-resizes each mask
onto its view, and writes PNG bytes under the original (e.g. .JPG) filename —
PIL sniffs content, not extension, and PGSR joins the images dir with the
COLMAP basename, so renaming to .png would break the dataset silently.

Masks are used TIGHT (no feather, no dilate): the same outlines the MILo
verdict used. Feathering would eat rim clay that sits inside the eroded edge.

Refuses loudly on any count/name/size mismatch instead of writing a partial set.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True, help="undistorted RGB views dir")
    ap.add_argument("--masks", required=True, help="L masks dir, named <view>.png")
    ap.add_argument("--out", required=True, help="output RGBA dir (created)")
    args = ap.parse_args()

    images = sorted(Path(args.images).glob("*.JPG"))
    if not images:
        print(f"no .JPG views in {args.images}", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)

    ref_size = Image.open(images[0]).size
    for im_path in images:
        mask_path = Path(args.masks) / (im_path.name + ".png")
        if not mask_path.exists():
            print(f"missing mask for {im_path.name} — refusing partial set", file=sys.stderr)
            return 1
        img = Image.open(im_path).convert("RGB")
        if img.size != ref_size:
            print(f"{im_path.name} is {img.size}, expected {ref_size}", file=sys.stderr)
            return 1
        mask = Image.open(mask_path).convert("L").resize(img.size, Image.NEAREST)
        img.putalpha(mask)
        img.save(out / im_path.name, format="PNG")

    # Coverage from the written files (reads back what PGSR will read).
    cov = []
    for im_path in images:
        a = Image.open(out / im_path.name).split()[3]
        h = a.histogram()
        cov.append(sum(h[128:]) / sum(h))
    n = len(cov)
    print(f"wrote {n} RGBA views to {out} at {ref_size}")
    print(f"alpha coverage mean {sum(cov)/n:.2%} min {min(cov):.2%} max {max(cov):.2%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
