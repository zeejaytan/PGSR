#!/usr/bin/env python3
"""Stage the QGS A03 trial root (R1 ticket 03).

QGS wants `<root>/images/` + `<root>/sparse/0/`, pre-undistorted bytes in
`<root>/images_undistorted_<downsample>/` (else its cv2 re-encode would drop
the RGBA alpha to JPEG). This stages a trial root of symlinks + byte copies
against the shared PGSR data WITHOUT touching it:

    <trial>/images              -> $DATA/images_rgba   (164 RGBA, alpha intact)
    <trial>/sparse/0/*.bin      -> $DATA/sparse/*.bin  (flat -> project layout)
    <trial>/images_undistorted_1.0/  byte copies of images/ (skips QGS re-encode)

Same pixels PGSR trained on (undistort would be a no-op for non-OPENCV; the
COLMAP model here is not re-undistorted anywhere in the M8 chain either, so
identical bytes = parity, stated not assumed).

Usage: python scripts/qgs_stage_a03.py <pgsr_data_A03_dir> <trial_dir>
Refuses loudly on wrong counts or missing alpha instead of staging silently.
"""
from __future__ import annotations

import os
import shutil
import sys

EXPECT = 164


def main() -> int:
    from PIL import Image

    if len(sys.argv) != 3:
        print("usage: qgs_stage_a03.py <pgsr_data_A03_dir> <trial_dir>", file=sys.stderr)
        return 1
    data, trial = sys.argv[1], sys.argv[2]

    rgba = os.path.join(data, "images_rgba")
    sparse = os.path.join(data, "sparse")
    names = sorted(f for f in os.listdir(rgba)
                   if f.lower().endswith((".jpg", ".jpeg", ".png")))
    if len(names) != EXPECT:
        print(f"images_rgba holds {len(names)} files, want {EXPECT} -- refusing",
              file=sys.stderr)
        return 1
    for need in ("cameras.bin", "images.bin", "points3D.bin"):
        if not os.path.isfile(os.path.join(sparse, need)):
            print(f"missing flat sparse/{need} -- refusing", file=sys.stderr)
            return 1
    # alpha spot-check: 3 files must carry a 4th band
    for probe in (names[0], names[len(names) // 2], names[-1]):
        with Image.open(os.path.join(rgba, probe)) as im:
            if len(im.getbands()) != 4:
                print(f"{probe} has bands {im.getbands()}, want RGBA -- refusing",
                      file=sys.stderr)
                return 1
    print(f"alpha spot-check ok on {names[0]}, mid, {names[-1]}")

    os.makedirs(trial, exist_ok=True)
    img_link = os.path.join(trial, "images")
    if not os.path.islink(img_link):
        os.symlink(rgba, img_link)
    s0 = os.path.join(trial, "sparse", "0")
    os.makedirs(s0, exist_ok=True)
    for need in ("cameras.bin", "images.bin", "points3D.bin"):
        dst = os.path.join(s0, need)
        if not os.path.islink(dst):
            os.symlink(os.path.join(sparse, need), dst)
    # byte copies: identical pixels, alpha intact, QGS skips its cv2 re-encode
    und = os.path.join(trial, "images_undistorted_1.0")
    os.makedirs(und, exist_ok=True)
    missing = [n for n in names if not os.path.isfile(os.path.join(und, n))]
    for n in missing:
        shutil.copyfile(os.path.join(rgba, n), os.path.join(und, n))
    have = len(os.listdir(und))
    if have != EXPECT:
        print(f"undistorted dir holds {have}, want {EXPECT} -- refusing", file=sys.stderr)
        return 1
    print(f"staged {trial}: images->images_rgba, sparse/0 compat links, "
          f"{EXPECT} undistorted byte copies ({len(missing)} copied this run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
