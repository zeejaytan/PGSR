#!/bin/bash
#SBATCH --job-name=qgs-extract-masked
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100-short
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=256G
#SBATCH --time=04:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/qgs_extract_masked_a03_%j.log

# Masked re-extraction of the finished QGS 30k model (R1 ticket 04 audit
# recovery). The stock `render.py` path fused UNMASKED (gt_alpha_mask is never
# assigned upstream), so this runs the PGSR-side port driver
# (scripts/qgs_run_extract_masked.py), which wires each camera's own alpha
# reader into the fusion gate before integrating. M8 parity: voxel 0.002 =
# 0.75 mm, sdf 5x voxel, depth_trunc 5.0, keep 10 clusters. Writes
# fuse_masked.ply (+ _post), never touching fuse.ply/fuse_post.ply.
#
# NOTE: the scheduler's lua hook bumps this to gpu-a100 full (256G exceeds
# the short partition's ~124G cap) — same as job 30829214. Same A100 cards.
#
# Usage: sbatch slurm/qgs_extract_masked_a03.slurm
set -euo pipefail

STATUS_DIR="/data/gpfs/projects/punim2657/PGSR/logs"
trap 'echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $?" >> "$STATUS_DIR/job_status.log"' EXIT

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
QGS_REPO=$PGSR_ROOT/qgs_trial/repo
OUT_DIR=$PGSR_ROOT/output/QGS_A03
ENV_PREFIX=$PGSR_ROOT/envs/qgs

echo "=== QGS A03 masked extraction started $(date) on $(hostname) ==="
nvidia-smi --query-gpu=memory.free --format=csv,noheader || true
free -g | head -2 || true

module purge
module load GCC/11.3.0 OpenMPI/4.1.4
module load CUDA/11.8.0
module load Miniforge3/24.7.1-2
export CUDA_HOME="${EBROOTCUDA:?}"
export LD_LIBRARY_PATH="$CUDA_HOME/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"

eval "$(conda shell.bash hook)"
# MKL/set -u guard: relax nounset for activation only.
set +u
conda activate "$ENV_PREFIX"
set -u
# Job 30887248 died in `import sqlite3` (via mediapy→IPython): the module
# stack's GCC 11.3.0 libstdc++ (first on LD_LIBRARY_PATH) lacks CXXABI_1.3.15
# that the env's own libicui18n needs. Prefer the env's newer libstdc++.
export LD_LIBRARY_PATH="$ENV_PREFIX/lib:${LD_LIBRARY_PATH:-}"

[[ -d "$OUT_DIR/point_cloud/iteration_30000" ]] || {
    echo "No finished 30k model at $OUT_DIR -- refusing" >&2; exit 1; }
[[ -f "$OUT_DIR/config.yaml" ]] || {
    echo "No saved config at $OUT_DIR/config.yaml -- refusing" >&2; exit 1; }

# Enter PGSR-side tooling without moving the QGS checkout:
# fetch this repo's main, take only slurm/ + scripts/.
PGSR_CHECKOUT=$PGSR_ROOT/repo
git -C "$PGSR_CHECKOUT" fetch origin main
git -C "$PGSR_CHECKOUT" checkout origin/main -- slurm scripts
DRIVER=$PGSR_CHECKOUT/scripts/qgs_run_extract_masked.py

cd "$QGS_REPO"
"$ENV_PREFIX/bin/python" "$DRIVER" --qgs_repo "$QGS_REPO" --model_dir "$OUT_DIR"

echo
echo "=== meshes produced ==="
find "$OUT_DIR" -name '*masked*.ply' -newermt '-1 day' | sort | tail -4
echo "=== QGS A03 masked extraction finished $(date) ==="
echo "Next: fetch fuse_masked_post.ply to artifacts/ and score it in ticket 04."
