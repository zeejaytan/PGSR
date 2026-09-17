#!/bin/bash
#SBATCH --job-name=qgs-extract-a03
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100-short
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=256G
#SBATCH --time=04:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/qgs_extract_a03_%j.log

# Fuse the QGS trial mesh at M8 parity (voxel 0.002 = 0.75 mm, sdf 5x voxel,
# depth_trunc 5.0, keep 10 clusters) from the finished 30k model. Prints free
# memory BEFORE the call so a crash reads as the known TSDF ceiling class.
#
# Usage: sbatch slurm/qgs_extract_a03.slurm
set -euo pipefail

STATUS_DIR="/data/gpfs/projects/punim2657/PGSR/logs"
trap 'echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $?" >> "$STATUS_DIR/job_status.log"' EXIT

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
QGS_REPO=$PGSR_ROOT/qgs_trial/repo
OUT_DIR=$PGSR_ROOT/output/QGS_A03
ENV_PREFIX=$PGSR_ROOT/envs/qgs

echo "=== QGS A03 extraction started $(date) on $(hostname) ==="
nvidia-smi --query-gpu=memory.free --format=csv,noheader || true
free -g | head -2 || true

module purge
module load GCC/11.3.0 OpenMPI/4.1.4
module load CUDA/11.8.0
module load Miniforge3/24.7.1-2
export CUDA_HOME="${EBROOTCUDA:?}"
export LD_LIBRARY_PATH="$CUDA_HOME/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"

eval "$(conda shell.bash hook)"
# Same MKL/set -u guard as the train script: relax nounset for activation only.
set +u
conda activate "$ENV_PREFIX"
set -u

[[ -d "$OUT_DIR/point_cloud/iteration_30000" ]] || {
    echo "No finished 30k model at $OUT_DIR -- refusing" >&2; exit 1; }
[[ -f "$OUT_DIR/config.yaml" ]] || {
    echo "No saved config at $OUT_DIR/config.yaml -- refusing" >&2; exit 1; }

cd "$QGS_REPO"
# skip_train + skip_test are True in qgs_a03.yaml: mesh only.
"$ENV_PREFIX/bin/python" render.py --conf_path "$OUT_DIR/config.yaml" --iteration 30000

echo
echo "=== meshes produced ==="
find "$OUT_DIR" -name '*.ply' -newermt '-1 day' | sort | tail -6
echo "=== QGS A03 extraction finished $(date) ==="
echo "Next: fetch the fused mesh to artifacts/ and score it in ticket 04."
