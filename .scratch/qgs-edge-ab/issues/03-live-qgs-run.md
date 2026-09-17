# 03: Live QGS train-plus-extract, one capture one seed

**What to build:** one pinned QGS training at full capture density plus one extraction at the same voxel with the stated masks — the only GPU the trial is allowed before scoring.

**Answers:** R1

**Blocked by:** 01 pin QGS source (GO required — missing mask construction stops here), 02 PGSR-A baseline (control must exist first).

**Status:** training batch 30694410 SUBMITTED (pending GPU grant) — laptop poll watching (5-min interval)

## Progress 2026-09-18 (env rebuilt, training submitted)

- Rebuild 30694282: COMPLETED exit 0 (~1 min RUNNING — caches held).
- Training **30694410** submitted on `gpu-a100` (12h wall, checkpoints 7k +
  30k); state PENDING (Priority) at submit. Staging re-runs as a no-op inside
  the job. Laptop poll watching; verdict checkpoint per the script: render
  held-out views at 7k vs 30k BEFORE fusing.

## Progress 2026-09-17 (resubmit: my cleanup error, env rebuild, training next)

- Agent error, stated plainly: while refreshing Spartan tooling I deleted the
  VERIFIED `envs/qgs` (complete cu118 build with numpy bridge confirmed
  in-holder). That cleanup step belongs to partial/failed envs only — this one
  was done. No data touched (trial staging, pins, scripts all intact); only the
  built environment needs re-creating from cache.
- Remediation: `slurm/qgs_build_env.slurm` (fixed script, `59c0689` refreshed on
  Spartan via fetch + checkout, fix confirmed at line 43) resubmitted as batch
  **30694282** on `gpu-a100-short` (2h wall). Package + wheel caches on GPFS
  survive, so the rebuild should run faster than the first build. Laptop poll
  watching (2-min interval).
- Training (`slurm/qgs_train_a03.slurm`, 12h, gpu-a100) goes in as the next
  command the moment 30694282 reports success, with its own laptop poll — no
  further approval needed (conservator: "resubmit training now" 2026-09-17).
- If the rebuild fails instead: read `logs/qgs_build_env_30694282.log` (+
  `pip_quad/pip_knn` logs) and report before touching anything else.

## Progress 2026-09-17 (train batch failed fast, fix pushed, needs approval)

- Batch 30635107 (12h, gpu-a100): FAILED after 6 s, exit 1 — log
  `logs/qgs_train_a03_30635107.log` dies at `conda activate` with
  `MKL_INTERFACE_LAYER: unbound variable`. Same MKL/`set -u` kill fixed in the
  build script (`a887161`) but never ported to the train script. Env, staging,
  and pins all intact (holder staging: 164 RGBA views, sparse/0 links,
  164 undistorted copies verified; `qgs_trial/data_A03/` holds
  images/images_undistorted_1.0/sparse). No GPU burned beyond the 6 s.
- Fix committed + pushed (`59c0689`): `set +u` / `set -u` guard around
  `conda activate` in BOTH `slurm/qgs_train_a03.slurm` and
  `slurm/qgs_extract_a03.slurm` (extract had the same latent bug), plus the
  EXIT-trap to `logs/job_status.log` per `docs/agents/slurm.md` (the failed job
  left no line there — that gap is now closed). `bash -n` clean on both.
- Resubmit path (needs explicit conservator approval per this ticket):
  Spartan checkout refreshes tooling via `fetch origin main` + `checkout
  origin/main -- slurm scripts` (detached HEAD, no pull), then
  `sbatch slurm/qgs_train_a03.slurm` + laptop-side poll. Staging re-runs as a
  no-op (0 copies). No holder needed — the 12h run outlasts any holder.

## Progress 2026-09-16 (holder granted, step 1 running)

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
- Grant arrived ~1h10 after request (short partition still queued behind
  Priority). Step 1 (`bash slurm/qgs_build_env.slurm` via `gpu_session.sh run`,
  fetch + checkout refreshed first) is running inside the holder with a laptop
  watcher; log `logs/qgs_build_env_30633299.log`.
- First step-1 attempt refused: cancelled batch 30633199 had started briefly
  before the scancel landed and recreated a partial `envs/qgs`. Removed it over
  ssh (holder still RUNNING) and relaunched step 1 — watcher on the retry.
- Relaunch FAILED on the real issue: `CONDA_OVERRIDE_CUDA=11.8` was ignored —
  solver still installed `pytorch 2.2.2 py3.9_cuda12.1`. Holder probe confirmed
  (`conda list`: `pytorch-cuda 12.1`). Fix committed (`b42ee60`):
  `conda search` shows `py3.9_cuda11.8_cudnn8.7.0_0` exists for the same pinned
  torch, so the script now injects `pytorch-cuda=11.8` into a generated copy of
  the pinned yml (anchor-checked, diff logged; upstream file untouched).
  Partial cu121 env cleared; step 1 relaunched in the holder with watcher.
- Relaunch 2 SOLVED the solver side (selector accepted, packages downloaded)
  but failed on a self-inflicted path bug: conda resolves `submodules/...` pip
  paths relative to the env FILE's directory, and the generated copy lives in
  logs/ — pip looked for `logs/submodules/...`. Fix committed (`0edbb6b`):
  absolutize both submodule paths in the generated file (anchor-checked, diff
  logged). Partial env cleared; step 1 relaunched in the holder with watcher.
- Relaunch 3 BUILT both wheels (cu118 torch + nvcc 11.8 match — the core
  problem is solved) but died one line later: `conda activate` under the
  script's `set -u`, killed by MKL's activate.d script referencing unset
  `MKL_INTERFACE_LAYER`. Fix committed (`a887161`): relax nounset for the
  activation line only. Env cleared for a clean single-log rerun (packages and
  pip wheels are cached, so the rerun is fast); step 1 relaunched with watcher.
- Relaunch 4 COMPLETE (`import ok`, `torch 2.2.2 cuda True`, exit 0): env
  `envs/qgs` built with cu118 torch, both CUDA extensions, open3d 0.18.
  Watch item: pip pulled numpy 2.0.2 over the yml's 1.26.4 and torch 2.2.2
  warns `_ARRAY_API not found` — `scripts/probe_torch_numpy.py` decides whether
  numpy goes back to the pinned 1.26.4 before any training.
- Probe DECIDED: `torch.from_numpy` raises `RuntimeError: Numpy is not
  available` under numpy 2.0.2 — training would crash on the first data load.
  Fix: restore the yml's own `numpy==1.26.4` after the pip installs (script
  change, same provenance as the rest of the build).
- Env VERIFIED in-holder: numpy 1.26.4, torch 2.2.2 cu118, from_numpy ok,
  open3d 0.18 ok, rasterizer+knn ok, cuda available True. Step 1 (env) done.
  Next: stage A03 data (step 2), then the single 30k training.
- Staging DONE in-holder: 164 RGBA views (alpha spot-check ok), sparse/0
  compat links, 164 undistorted byte copies — shared data untouched.
- Training SUBMITTED as batch 30635107 (12h wall, gpu-a100, checkpoints at 7k
  + 30k) with explicit conservator approval: the run needs no interaction and
  outlasts the holder (~18:40 expiry). Laptop poll watching (5-min interval).

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
