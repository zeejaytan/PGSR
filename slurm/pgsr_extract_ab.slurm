#!/bin/bash
#SBATCH --job-name=pgsr-extract-ab
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100-short
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=04:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_extract_ab_%j.log

# Extract BOTH trial variants from one trained model, back to back.
# Variant A (fusion-masked): images_rgba in, masks zero background depth at
# fusion. Variant B (cull-after): plain images in, rig removed only by the
# post-fusion cluster filter. Same training, same voxel, mask is the variable.
# Outputs are archived per variant immediately — both runs write the same
# model-relative paths and would otherwise overwrite each other.
#
# Usage: sbatch slurm/pgsr_extract_ab.slurm <model_dir_name> [voxel] [clusters]
#   e.g. sbatch slurm/pgsr_extract_ab.slurm A03_noreg
#        sbatch slurm/pgsr_extract_ab.slurm A03_noreg 0.002 10
set -euo pipefail

MODEL="${1:?usage: sbatch pgsr_extract_ab.slurm <model_dir_name> [voxel] [clusters]}"
VOXEL="${2:-0.002}"
NCLUSTER="${3:-10}"

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
DATA_DIR=$PGSR_ROOT/data/17062025/A03
OUT_DIR=$PGSR_ROOT/output/$MODEL

echo "=== PGSR A/B extraction from $MODEL started $(date) on $(hostname) ==="
echo "voxel $VOXEL scene-units, keep $NCLUSTER clusters, max_depth 5.0 (default)"
nvidia-smi --query-gpu=memory.free --format=csv,noheader || true
free -g | head -2 || true

module purge
module load GCC/11.3.0 OpenMPI/4.1.4
module load CUDA/11.8.0
module load Miniforge3/24.7.1-2
export CUDA_HOME="${EBROOTCUDA:?}"
export LD_LIBRARY_PATH="$CUDA_HOME/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

[[ -d "$OUT_DIR/point_cloud/iteration_30000" ]] || {
    echo "No finished 30k model at $OUT_DIR" >&2; exit 1; }
grep -q "linalg.inv(pose)" "$REPO_DIR/render.py" || {
    echo "render.py lacks the C2W fork fix — refusing to fuse wrong-frame meshes" >&2; exit 1; }

cd "$REPO_DIR"
PY="$ENV_PREFIX/bin/python"

echo
echo "=== variant A: fusion-masked ==="
$PY render.py -s "$DATA_DIR" -m "$OUT_DIR" -i images_rgba -r 1 \
    --iteration 30000 --voxel_size "$VOXEL" --num_cluster "$NCLUSTER" --skip_test
mv "$OUT_DIR/mesh" "$OUT_DIR/mesh_A_masked"
mv "$OUT_DIR/train/ours_30000" "$OUT_DIR/train_A_ours_30000"

echo
echo "=== variant B: cull-after (unmasked) ==="
$PY render.py -s "$DATA_DIR" -m "$OUT_DIR" -i images -r 1 \
    --iteration 30000 --voxel_size "$VOXEL" --num_cluster "$NCLUSTER" --skip_test
mv "$OUT_DIR/mesh" "$OUT_DIR/mesh_B_cullafter"

echo
echo "=== meshes produced ==="
$PY scripts/mesh_stats.py "$OUT_DIR/mesh_A_masked" "$OUT_DIR/mesh_B_cullafter"
echo "=== A/B extraction finished $(date) ==="
echo "Next: draw both meshes before reading numbers off them."
