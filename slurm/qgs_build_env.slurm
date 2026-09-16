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
# Torch/CUDA parity (jobs 30557071, holder 30633299): QGS environment.yml pins
# torch 2.2.2, and conda resolves it to the cu121 build (torch.version.cuda
# 12.1), while the PGSR-parity module stack here loads CUDA 11.8.
# torch's cpp_extension refuses any mismatch, so both CUDA wheels failed.
# CONDA_OVERRIDE_CUDA=11.8 was tried and IGNORED (solver still picked
# py3.9_cuda12.1). The fix that works on this solver: add the `pytorch-cuda`
# selector metapackage, the documented conda-native way to pick a CUDA flavor.
# Verified `conda search` offers pytorch 2.2.2 py3.9_cuda11.8_cudnn8.7.0_0, so
# the pinned torch version is unchanged — only the CUDA flavor is selected.
# The pinned upstream file is never edited: the selector is injected into a
# generated copy (diff it against the pin in the log). Same precedent as the
# MILo env (torch cu118 + CUDA 11.8, builds fine).

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

# Build the effective env file: pinned upstream yml + the CUDA-flavor selector.
# Anchor on the exact pinned lines; refuse if the upstream file ever drifts.
# Two rewrites, both logged by diff below: (1) add `pytorch-cuda=11.8`;
# (2) absolutize the `submodules/...` pip paths — conda resolves them relative
# to the env FILE's directory, and this generated copy lives in logs/ (holder
# 30633299: relative paths made pip look for logs/submodules/...).
ENV_YML="$STATUS_DIR/qgs_env_11.8_${SLURM_JOB_ID:?}.yml"
grep -qx '  - pytorch=2.2.2' "$QGS_REPO/environment.yml" \
    || { echo "anchor 'pytorch=2.2.2' not found in pinned environment.yml -- refusing" >&2; exit 1; }
grep -qx '    - submodules/diff-quadratic-rasterization' "$QGS_REPO/environment.yml" \
    || { echo "anchor submodule paths not found in pinned environment.yml -- refusing" >&2; exit 1; }
sed -e 's/^  - pytorch=2.2.2$/  - pytorch=2.2.2\n  - pytorch-cuda=11.8/' \
    -e "s|^    - submodules/|    - $QGS_REPO/submodules/|" \
    "$QGS_REPO/environment.yml" > "$ENV_YML"
diff <(grep -v '^name:' "$QGS_REPO/environment.yml") <(grep -v '^name:' "$ENV_YML") \
    || true  # the ONLY intended differences are the selector + 2 absolute paths
grep -qx '  - pytorch-cuda=11.8' "$ENV_YML" \
    || { echo "selector injection failed -- refusing" >&2; exit 1; }
grep -q "    - $QGS_REPO/submodules/diff-quadratic-rasterization" "$ENV_YML" \
    && grep -q "    - $QGS_REPO/submodules/simple-knn" "$ENV_YML" \
    || { echo "submodule path absolutization failed -- refusing" >&2; exit 1; }
echo "effective env file: $ENV_YML (pinned yml + pytorch-cuda=11.8 + absolute submodule paths)"

conda env create -p "$ENV_PREFIX" -f "$ENV_YML"
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
