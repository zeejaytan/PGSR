#!/bin/bash
#SBATCH --job-name=pgsr-train-noreg
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=12:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_train_noreg_%j.log

# Full 30k training with PGSR's geometric regularization OFF.
# Probe (output/A03_probe_noreg, 7k) showed the planar single-view +
# multi-view NCC/geometric losses smear this material (15.5 dB with, 22.9 dB
# without on the same 21 held-out views); plain photometric training finds the
# rig crisply. One variable differs from pgsr_train.slurm; exposure stays off
# for the same isolation reason (follow-up arm if this plateaus).
#
# Usage: sbatch slurm/pgsr_train_noreg.slurm
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
DATA_DIR=$PGSR_ROOT/data/17062025/A03
OUT_DIR=$PGSR_ROOT/output/A03_noreg

echo "=== PGSR noreg training on A03 started $(date) on $(hostname) ==="
nvidia-smi | head -15 || true

module purge
module load GCC/11.3.0 OpenMPI/4.1.4
module load CUDA/11.8.0
module load Miniforge3/24.7.1-2
export CUDA_HOME="${EBROOTCUDA:?}"
export LD_LIBRARY_PATH="$CUDA_HOME/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

"$ENV_PREFIX/bin/python" -c "import diff_plane_rasterization" || {
    echo "plane rasterizer missing — run slurm/pgsr_build_ext.slurm first" >&2; exit 1; }

[ -f "$DATA_DIR/provenance.json" ] || { echo "No dataset at $DATA_DIR" >&2; exit 1; }
[ -f "$DATA_DIR/sparse/images.bin" ] || { echo "No COLMAP model at $DATA_DIR/sparse/images.bin (PGSR reads a FLAT sparse/, not sparse/0)" >&2; exit 1; }
[ -n "$(ls -A "$DATA_DIR/images_rgba")" ] || { echo "Empty image set at $DATA_DIR/images_rgba" >&2; exit 1; }

if [[ -d "$OUT_DIR/point_cloud/iteration_30000" ]]; then
    echo "$OUT_DIR already holds a finished 30k run." >&2
    exit 1
fi

mkdir -p "$OUT_DIR"
cd "$REPO_DIR"

# -r 1 : full resolution (default -1 silently downsamples past 1600 px).
# --eval : hold out every 8th view for honest renders.
# regs off : the one variable under test (see header).
"$ENV_PREFIX/bin/python" train.py \
    -s "$DATA_DIR" \
    -m "$OUT_DIR" \
    -i images_rgba \
    -r 1 \
    --eval \
    --single_view_weight 0 \
    --multi_view_ncc_weight 0 \
    --multi_view_geo_weight 0

echo
echo "=== point clouds produced ==="
find "$OUT_DIR" -name 'iteration_*' -newermt '-1 day' | sort | tail -4
echo "=== PGSR noreg training on A03 finished $(date) ==="
echo "Next: render.py both variants from this model, then compare."
