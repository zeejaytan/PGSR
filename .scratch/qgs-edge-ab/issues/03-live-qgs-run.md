# 03: Live QGS train-plus-extract, one capture one seed

**What to build:** one pinned QGS training at full capture density plus one extraction at the same voxel with the stated masks — the only GPU the trial is allowed before scoring.

**Answers:** R1

**Blocked by:** 01 pin QGS source (GO required — missing mask construction stops here), 02 PGSR-A baseline (control must exist first).

**Status:** claimed — env build job 30542583 running (fix for quota failure below)

## Progress 2026-09-14

- Job 30522489 (env build, old script): FAILED after ~90 s — `~/.conda/pkgs`
  extracts died with `Errno 122 Disk quota exceeded` (home at 51200M/51200M).
- Home cleaned 2026-09-14: `conda clean --all` freed ~10 GB (51200M → 41016M,
  pkgs 1046 → 214 entries). Four legacy home envs left in place
  (`blender-render`, `breaking-bad`, `fracture-modes`, `puzzlefusionpp`).
- Fix committed (`d5aeadf`): `slurm/qgs_build_env.slurm` exports
  `CONDA_PKGS_DIRS=$PGSR_ROOT/conda_pkgs`. Umbrella rule written to
  `docs/agents/slurm.md` + `CLAUDE.local.md`: project storage under
  `/data/gpfs/projects/punim2657/`, never home.
- Submit note: Spartan checkout is detached at stock pin by design — `git pull`
  fails there; tooling enters via `git fetch origin main` + `git checkout
  origin/main -- slurm scripts`. Job 30542576 (old script) cancelled,
  30542583 (fixed script) submitted, laptop poll running.

## Progress 2026-09-14 (env build failed at pip, holder opened)

- Job 30542583: FAILED after ~5 min RUNNING (1.5 h queue). Conda env create
  succeeded (pkgs fix worked); `pip install` of both CUDA submodules failed
  with hidden output (`finished with status 'error'`, no compiler message —
  pip suppresses it). glm submodule present; `envs/qgs` partial env remains.
- This is now the iterative case: holder session for debug (one queue wait,
  then free retries) instead of another sbatch per attempt.
  `scripts/gpu_session.sh` copied from umbrella; step 1 = verbose pip
  reinstall surfacing the real nvcc error.

- [ ] Single QGS training on `A03_sherds` at full resolution (no silent downsample), one seed, run values as pinned in 01; held-out views kept honest where the build supports them
- [ ] Single extraction at the stated voxel/band in mm with the stated mask construction; block counts and free-memory figures printed before the call; training-time masking and post-training pruning untouched per M4/M5
- [ ] Outputs archived without overwriting each other; mesh stats (verts, pieces, bounds vs training points) printed; no batch submission without explicit approval, laptop-side poll on the submit
- [ ] A block/OOM-class crash is recorded as the known ceiling (R1 becomes the tiling question by amendment), not a new mystery and not a silent workaround
