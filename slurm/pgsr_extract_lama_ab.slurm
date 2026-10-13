#!/bin/bash
#SBATCH --job-name=pgsr-extract-lama-ab
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100-short
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=256G
#SBATCH --time=04:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_extract_lama_ab_%j.log

# Fuse BOTH lama-face-fill trial arms from their finished 30k trainings.
# Arm A (LaMa-inpainted inputs) and arm B (unmasked control) fuse with the
# SAME stock construction: unmasked inputs, full resolution, voxel 0.002
# scene-units (stock render.py 4x -> sdf_trunc 0.008), 10 clusters.
# render.py is untouched (spec: LaMa arm alters photographs, not the loss).
#
# Usage: sbatch slurm/pgsr_extract_lama_ab.slurm [voxel] [clusters]
#   e.g. sbatch slurm/pgsr_extract_lama_ab.slurm
#        sbatch slurm/pgsr_extract_lama_ab.slurm 0.002 10
# Subset: VARIANTS="A B" (default) — an arm whose fused mesh already exists
# is skipped loudly, so resubmits cost nothing.
set -euo pipefail

VOXEL="${1:-0.002}"
NCLUSTER="${2:-10}"
VARIANTS="${VARIANTS:-A B}"

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo

# arm -> "data_dir|output_dir"
declare -A ARMS=(
    [A]="$PGSR_ROOT/data/17062025/A31_lama|$PGSR_ROOT/output/A31A_lama"
    [B]="$PGSR_ROOT/data/17062025/A31_control|$PGSR_ROOT/output/A31B_ctrl"
)

echo "=== PGSR lama A/B extraction started $(date) on $(hostname) ==="
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

grep -q "linalg.inv(pose)" "$REPO_DIR/render.py" && {
    echo "render.py contains the withdrawn C2W invert — refusing to fuse displaced meshes" >&2; exit 1; }

cd "$REPO_DIR"
PY="$ENV_PREFIX/bin/python"

for ARM in A B; do
if [[ " $VARIANTS " != *" $ARM "* ]]; then
    echo "(arm $ARM not in VARIANTS=$VARIANTS — skipping.)"
    continue
fi
IFS='|' read -r DATA_DIR OUT_DIR <<< "${ARMS[$ARM]}"
echo
echo "=== arm $ARM: data $DATA_DIR -> model $OUT_DIR ==="
[[ -d "$OUT_DIR/point_cloud/iteration_30000" ]] || {
    echo "No finished 30k model at $OUT_DIR" >&2; exit 1; }
[[ -f "$DATA_DIR/sparse/images.bin" ]] || {
    echo "No COLMAP model at $DATA_DIR/sparse/images.bin" >&2; exit 1; }
if [[ -f "$OUT_DIR/mesh/tsdf_fusion_post.ply" ]]; then
    echo "arm $ARM mesh/tsdf_fusion_post.ply already fused — skipping (delete it to re-run)."
    continue
fi
$PY render.py -s "$DATA_DIR" -m "$OUT_DIR" -i images -r 1 \
    --iteration 30000 --voxel_size "$VOXEL" --num_cluster "$NCLUSTER" --skip_test
done

echo
echo "=== meshes produced ==="
$PY scripts/mesh_stats.py \
    "$PGSR_ROOT/output/A31A_lama/mesh" \
    "$PGSR_ROOT/output/A31B_ctrl/mesh"
echo "=== lama A/B extraction finished $(date) ==="
echo "Next: draw both meshes before reading numbers off them."
