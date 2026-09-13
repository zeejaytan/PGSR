#!/bin/bash
#SBATCH --job-name=qgs-build-env
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/qgs_build_env_%j.log

# Fresh QGS conda env (NOT an MILo-env delta: python 3.9.19 + torch 2.2.2 pins
# differ, reuse-first probe fails by inspection) + both CUDA submodule builds.
# Runs on gpu-a100 for module-stack parity with the training job, like the
# PGSR ext build before it. Refuses if the env already exists.
set -euo pipefail

QGS_PIN=74d05c945e99fcaef7afe5a8831903be71ad9b55
PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
QGS_REPO=$PGSR_ROOT/qgs_trial/repo
ENV_PREFIX=$PGSR_ROOT/envs/qgs

echo "=== QGS env build started $(date) on $(hostname) ==="

module purge
module load GCC/11.3.0 OpenMPI/4.1.4
module load CUDA/11.8.0
module load Miniforge3/24.7.1-2
export CUDA_HOME="${EBROOTCUDA:?}"
export LD_LIBRARY_PATH="$CUDA_HOME/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"
export TORCH_CUDA_ARCH_LIST="8.0"

command -v nvcc || { echo "nvcc missing -- refusing" >&2; exit 1; }
eval "$(conda shell.bash hook)"

if [[ -d "$ENV_PREFIX" ]]; then
    echo "$ENV_PREFIX exists -- refusing (delete it to rebuild)." >&2; exit 1
fi
[[ -d "$QGS_REPO/.git" ]] || { echo "no QGS checkout at $QGS_REPO -- refusing" >&2; exit 1; }
HAVE=$(git -C "$QGS_REPO" rev-parse HEAD)
[[ "$HAVE" == "$QGS_PIN" ]] || { echo "checkout at $HAVE, want $QGS_PIN -- refusing" >&2; exit 1; }
echo "checkout pinned at $HAVE"

conda env create -p "$ENV_PREFIX" -f "$QGS_REPO/environment.yml"
conda activate "$ENV_PREFIX"
pip install "$QGS_REPO/submodules/diff-quadratic-rasterization"
pip install "$QGS_REPO/submodules/simple-knn"

"$ENV_PREFIX/bin/python" -c \
  "import torch, open3d; import diff_quadratic_rasterization, simple_knn; \
   print('torch', torch.__version__, 'cuda', torch.cuda.is_available()); \
   print('import ok')"
echo "=== QGS env build finished $(date) ==="
echo "Next: slurm/qgs_train_a03.slurm (single 30k training, one seed)."
