#!/bin/bash
#SBATCH --job-name=pgsr-build-p3d
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_build_p3d_%j.log

# Build pytorch3d from source into the SHARED envs/milo conda env.
# Additive delta only, pinned tag. Needed: PGSR's gaussian_model.py imports
# quaternion_to_matrix at module top (load-bearing in densification), and no
# official wheel exists for this env's combo (torch 2.3.1 + CUDA 11.8 + py3.9).
#
# The compile needs no GPU device, but runs on the gpu-a100 module stack so the
# extension builds against the CUDA it will run against. TORCH_CUDA_ARCH_LIST
# restricts the build to A100 (sm_80); a full-arch build takes several times
# longer for cards that will never run it.
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
P3D_TAG="${P3D_TAG:-v0.7.7}"
SRC_DIR=$PGSR_ROOT/build/pytorch3d

echo "=== pytorch3d build started $(date) on $(hostname) ==="

module purge
module load GCC/11.3.0 OpenMPI/4.1.4
module load CUDA/11.8.0
module load Miniforge3/24.7.1-2
export CUDA_HOME="${EBROOTCUDA:?}"
export LD_LIBRARY_PATH="$CUDA_HOME/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"

command -v nvcc || { echo "nvcc not on PATH after module loads — refusing" >&2; exit 1; }

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

cd /tmp
"$ENV_PREFIX/bin/python" -c "import pytorch3d" 2>/dev/null && {
    echo "pytorch3d already imports — nothing to build."; exit 0; }

if [[ ! -d "$SRC_DIR/.git" ]]; then
    git clone -q --branch "$P3D_TAG" --depth 1 https://github.com/facebookresearch/pytorch3d.git "$SRC_DIR"
fi
git -C "$SRC_DIR" rev-parse HEAD

cd "$SRC_DIR"
export MAX_JOBS=8
export TORCH_CUDA_ARCH_LIST="8.0"
"$ENV_PREFIX/bin/pip" install --no-build-isolation .

cd /tmp
"$ENV_PREFIX/bin/python" -c "import pytorch3d; print('import ok:', pytorch3d.__version__)"
echo "=== build finished $(date) ==="
