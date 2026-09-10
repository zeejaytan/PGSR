#!/bin/bash
#SBATCH --job-name=pgsr-train-a03
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=12:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_train_a03_%j.log

# Train stock PGSR once on the sherd-only A03 set, full resolution, every-8th
# view held out. ONE training serves both trial variants: the mask lives only
# in RGBA alpha and is consumed solely at fusion (render.py:120-121), so
# training on RGBA optimises the identical pixels as training on RGB.
#
# Usage: sbatch slurm/pgsr_train.slurm
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
DATA_DIR=$PGSR_ROOT/data/17062025/A03
OUT_DIR=$PGSR_ROOT/output/A03

echo "=== PGSR training on A03 started $(date) on $(hostname) ==="
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

# Refuse to start on top of a finished run rather than discover afterwards
# that the mesh being compared was overwritten halfway through.
if [[ -d "$OUT_DIR/point_cloud/iteration_30000" ]]; then
    echo "$OUT_DIR already holds a finished 30k run." >&2
    exit 1
fi

mkdir -p "$OUT_DIR"
cd "$REPO_DIR"

# -r 1 : full resolution. The default (-1) silently downsamples anything wider
#        than 1600 px (utils/camera_utils.py) — same trap as MILo.
# --eval : hold out every 8th view (scene/dataset_readers.py, llffhold=8).
#          Those views are the only honest instrument at comparison time.
# 30k iterations is the upstream default; test/save renders at 7k and 30k.
"$ENV_PREFIX/bin/python" train.py \
    -s "$DATA_DIR" \
    -m "$OUT_DIR" \
    -i images_rgba \
    -r 1 \
    --eval

echo
echo "=== point clouds produced ==="
find "$OUT_DIR" -name 'iteration_*' -newermt '-1 day' | sort | tail -4
echo "=== PGSR training on A03 finished $(date) ==="
echo "Next: render.py both variants (fusion-masked + cull-after), then compare."
