#!/bin/bash
#SBATCH --job-name=qgs-build-env
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100-short
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/qgs_build_env_%j.log

# Fresh QGS conda env (NOT an MILo-env delta: python 3.9.19 + torch 2.2.2 pins
# differ, reuse-first probe fails by inspection) + both CUDA submodule builds.
# Runs on gpu-a100-short: same A100 cards as the training job (module-stack
# parity, like the PGSR ext build before it) with a faster grant; 2h fits the
# 4h short wall. Refuses if the env already exists.
set -euo pipefail

STATUS_DIR="/data/gpfs/projects/punim2657/PGSR/logs"
trap 'echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $?" >> "$STATUS_DIR/job_status.log"' EXIT

QGS_PIN=74d05c945e99fcaef7afe5a8831903be71ad9b55
PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
QGS_REPO=$PGSR_ROOT/qgs_trial/repo
ENV_PREFIX=$PGSR_ROOT/envs/qgs
# Home quota is full (50G used, job 30522489 died extracting pkgs there):
# keep the multi-GB package cache on project storage instead.
export CONDA_PKGS_DIRS="$PGSR_ROOT/conda_pkgs"
mkdir -p "$CONDA_PKGS_DIRS" "$(dirname "$ENV_PREFIX")"
# Torch/CUDA parity (job 30557071): QGS environment.yml pins torch 2.2.2, and
# conda resolves it to the cu121 build (torch.version.cuda 12.1), while the
# PGSR-parity module stack here loads CUDA 11.8. torch's cpp_extension refuses
# any mismatch, so both CUDA wheels failed. The MILo env precedent is
# torch cu118 + CUDA 11.8 (works). Override the solver's detected CUDA so it
# picks the cu118 build of the same pinned torch, matching the nvcc below.
export CONDA_OVERRIDE_CUDA="11.8"

echo "=== QGS env build started $(date) on $(hostname) ==="

module purge
module load GCC/11.3.0 OpenMPI/4.1.4
module load CUDA/11.8.0
module load Miniforge3/24.7.1-2
export CUDA_HOME="${EBROOTCUDA:?}"
export LD_LIBRARY_PATH="$CUDA_HOME/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"
export TORCH_CUDA_ARCH_LIST="8.0"

command -v nvcc || { echo "nvcc missing -- refusing" >&2; exit 1; }
nvcc --version | tail -1
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
# -v: pip hides the compiler error by default (job 30542583 failed both
# wheels with no message). Full output lands on GPFS; console keeps the tail.
pip install -v "$QGS_REPO/submodules/diff-quadratic-rasterization" 2>&1 \
    | tee "$STATUS_DIR/pip_quad_$SLURM_JOB_ID.log" | tail -n 15
pip install -v "$QGS_REPO/submodules/simple-knn" 2>&1 \
    | tee "$STATUS_DIR/pip_knn_$SLURM_JOB_ID.log" | tail -n 15

"$ENV_PREFIX/bin/python" -c \
  "import torch, open3d; import diff_quadratic_rasterization, simple_knn; \
   print('torch', torch.__version__, 'cuda', torch.cuda.is_available()); \
   print('import ok')"
echo "=== QGS env build finished $(date) ==="
echo "Next: slurm/qgs_train_a03.slurm (single 30k training, one seed)."
