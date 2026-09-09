#!/bin/bash
#SBATCH --job-name=pgsr-build-ext
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_build_ext_%j.log

# Compile PGSR's plane rasterizer into the SHARED envs/milo conda env.
# Additive delta only: the env already carries torch, simple_knn, fused_ssim,
# open3d. No fresh env. (Ticket 02 probe: only diff_plane_rasterization missing.)
#
# The compile itself needs no GPU device, but this runs on the same gpu-a100
# module stack the training job will use, so the CUDA the extension builds
# against is the CUDA it runs against.
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo

echo "=== PGSR extension build started $(date) on $(hostname) ==="

module purge
module load GCC/11.3.0 OpenMPI/4.1.4
module load CUDA/11.8.0
module load Miniforge3/24.7.1-2
export CUDA_HOME="${EBROOTCUDA:?}"
export LD_LIBRARY_PATH="$CUDA_HOME/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"

command -v nvcc || { echo "nvcc not on PATH after module loads — refusing" >&2; exit 1; }
nvcc --version | tail -1

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

"$ENV_PREFIX/bin/python" -c "import diff_plane_rasterization" 2>/dev/null && {
    echo "diff_plane_rasterization already imports — nothing to build."; exit 0; }

cd "$REPO_DIR/submodules/diff-plane-rasterization"
"$ENV_PREFIX/bin/pip" install --no-build-isolation .

"$ENV_PREFIX/bin/python" -c "import diff_plane_rasterization; print('import ok')"
echo "=== build finished $(date) ==="
