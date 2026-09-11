# AGENTS.md — PGSR / sherd surfacing (project)

Follow the workspace root **`../AGENTS.md`** (laptop ↔ GitHub ↔ Spartan) for all shared
rules. This file only adds PGSR-specific paths and domain notes.

## What this repo is for

Judging standalone PGSR (planar-based Gaussian splatting plus its TSDF fusion) as a
sherd mesh route on Rabati turntable photographs, on the same ruler as the MILo fork
and the COLMAP → OpenMVS route. PGSR lives here as a sibling of MILo, never inside it:
the MILo fork tracks a different upstream method and its rebase-survival list gains
nothing from this work.

First question answered here: MILo `intent/M8` (does PGSR replace MILo at the
resolution a break face needs?). New questions opened here take prefix **`R`**.

## Paths

| Role | Value |
|------|--------|
| GitHub fork (`origin`) | `zeejaytan/PGSR` |
| Upstream | `zju3dv/PGSR` (read-only) plus the community masked-fusion construction, pinned per ticket |
| Spartan checkout (`REMOTE_ROOT`) | `/data/gpfs/projects/punim2657/PGSR/repo` — detached at the pinned stock commit for trials; slurm tooling enters via `git fetch origin main` + `git checkout origin/main -- slurm scripts`, never a pull that moves HEAD |
| Spartan working area (untracked) | `/data/gpfs/projects/punim2657/PGSR/` — holds `data/`, `output/`, `logs/` |
| Compute env (reuse-first) | the existing MILo conda env, which carries everything except the plane rasterizer. One additive build (`slurm/pgsr_build_ext.slurm`) compiles `diff-plane-rasterization` into it; no fresh env |
| SSH | `Host spartan`, user `zhuojiat` |
| Remote helpers | `scripts/remote/pull_and_sbatch.sh`, `job_status.sh`, `fetch_artifacts.sh` |

Default branch is **`main`** (align with the upstream default at fork time if it differs).
Local rsync landing zone: `artifacts/` — comparison renders, metrics and logs only.

## Write rules

Analysis/build code → `scripts/`; versioned Slurm → `slurm/`; method notes → `docs/notes/`;
what we are trying to establish → `intent/`; fetched samples → `artifacts/` (not source);
HPC paths → `CLAUDE.local.md`. Do not add files at the repo root beyond the standing set.

## Fork changes against upstream

Keep this list current; it is what a rebase onto upstream has to survive.

1. **`render.py` — fuse through camera-to-world, not its inverse.** Upstream builds
   `pose` as COLMAP world-to-camera (`view.R` stored transposed, un-transposed at
   use) and hands it to Open3D `integrate()`, which takes camera-to-world. The
   extracted mesh then lands in the wrong frame — proven on A03 by
   `scripts/probe_fusion_pose.py` (0/61590 points forward under the assumed
   camera vs 85.1% under COLMAP control) with both trial meshes landing 0%
   inside the OpenMVS reference box. One-line `[PGSR FORK]` invert. Training is
   untouched (the rasterizer path is self-consistent); only the fused mesh moves.

## Domain notes

- The renderer file vendored inside MILo is not standalone PGSR. Verdicts here pin
  stock upstream and the community masked-fusion construction separately, before any job.
- Masking here means fusion-time outlines deciding what counts as clay when depth enters
  the grid, plus a post-fusion small-component filter for the stock variant.
  Training-time masking and post-training splat pruning stay retired (MILo M4/M5)
  without fresh justification.
- A splat is judged on renders, never in millimetres. No ground truth exists for a
  Rabati sherd; compare routes against each other on the same capture and ruler.

## Agent skills

- **Issue tracker — local markdown.** Spec at `.scratch/<feature>/spec.md`, tickets at
  `.scratch/<feature>/issues/<NN>-<slug>.md` from `01`, each carrying an **`Answers:`**
  line (`R1` here once opened, `M8` for the first verdict). Conventions:
  `../docs/agents/issue-tracker.md`.
- **Triage labels.** `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`,
  `wontfix`, as a `Status:` line. Details: `../docs/agents/triage-labels.md`.
- **Intent.** [`intent/`](intent/) holds what we are trying to establish — prefix **`R`**,
  permanent, numbers never reused. Check the loop with
  `python ../scripts/check_intent_links.py`.

**Do not run `/setup-matt-pocock-skills` in this repo.**
