# 03: Live QGS train-plus-extract, one capture one seed

**What to build:** one pinned QGS training at full capture density plus one extraction at the same voxel with the stated masks — the only GPU the trial is allowed before scoring.

**Answers:** R1

**Blocked by:** 01 pin QGS source (GO required — missing mask construction stops here), 02 PGSR-A baseline (control must exist first).

**Status:** holder session 30633299 requested (interactive, replaces batch) — waiting for grant

## Progress 2026-09-16 (holder replaces batch)

- Batch 30633199 (cu118 fix) cancelled while PENDING — per conservator: use a
  holder, the env build may need iterative work.
- First holder request 30633296 landed on `gpu-a100` full: the session script
  defaults to 16 CPU / 128 GB, and the submit hook bumps anything over 8 CPUs
  off short. Cancelled; re-requested as 30633299 with `CPUS=8 MEM=64G` (covers
  step 1 env build), holding on `gpu-a100-short` for the faster grant.
- Watcher running on the laptop; grant notifies like a poll. First command
  inside once granted: the env build (step 1 only), via
  `srun --jobid=<id> --overlap` per `scripts/gpu_session.sh run`.
- Note: the watcher for cancelled 30633296 never exits on its own (loops on
  GONE) — harmless ssh noise, dies with the laptop session; ignore it.

## Progress 2026-09-16 (env build failed on CUDA mismatch, fix committed)

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

## Progress 2026-09-14 (holder cancelled, batch on short)

- Holder 30546110 (gpu-a100 full) cancelled before grant — laptop going to
  sleep, so a held node would idle unwatched. Batch job 30557071 submitted on
  `gpu-a100-short` (same A100 cards, 2h fits 4h wall).
- Script audit before submit (`d6b5b71`): partial `envs/qgs` removed (old
  script would have refused); `CONDA_PKGS_DIRS` on GPFS kept; EXIT trap appends
  to `logs/job_status.log` (poll dies with laptop — log is source of truth);
  `nvcc --version` printed (CUDA 11.8 vs torch cu121 is the open suspect);
  `pip install -v` with full output teed to `logs/pip_{quad,knn}_$JOB.log`.
- Morning check: `sacct -j 30557071` + `tail logs/job_status.log`; on failure
  read `logs/pip_quad_30557071.log` for the nvcc error.

## Progress 2026-09-16 (morning check result)

- Job 30557071: FAILED after ~2 min. No `logs/pip_quad_30557071.log` exists —
  the failure is inside `conda env create` itself (environment.yml pip section
  builds both wheels), before the script's explicit pip lines run.
- Cause (log lines 101-106): `RuntimeError: detected CUDA 11.8 mismatches the
  version used to compile PyTorch (12.1)`. Conda resolved torch 2.2.2 to cu121
  while the script loads CUDA/11.8.0. The open suspect from 09-14 is confirmed.
  Precedent: MILo env torch is 2.3.1+cu118 and builds fine on CUDA 11.8.
- Fix: `slurm/qgs_build_env.slurm` now exports `CONDA_OVERRIDE_CUDA="11.8"` so
  the solver picks the cu118 build of the same pinned torch 2.2.2, matching
  nvcc 11.8. No pin change, same A100 module stack as PGSR.
- Partial `envs/qgs` must be removed on Spartan before resubmit (script refuses
  when it exists). Resubmit via fetch + `checkout origin/main -- slurm scripts`
  (detached checkout, no pull), then sbatch + laptop poll.

- [ ] Single QGS training on `A03_sherds` at full resolution (no silent downsample), one seed, run values as pinned in 01; held-out views kept honest where the build supports them
- [ ] Single extraction at the stated voxel/band in mm with the stated mask construction; block counts and free-memory figures printed before the call; training-time masking and post-training pruning untouched per M4/M5
- [ ] Outputs archived without overwriting each other; mesh stats (verts, pieces, bounds vs training points) printed; no batch submission without explicit approval, laptop-side poll on the submit
- [ ] A block/OOM-class crash is recorded as the known ceiling (R1 becomes the tiling question by amendment), not a new mystery and not a silent workaround
