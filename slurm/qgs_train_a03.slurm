#!/bin/bash
#SBATCH --job-name=qgs-train-a03
#SBATCH --account=punim2657
#SBATCH --partition=gpu-a100
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=14:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/qgs_train_a03_%j.log

# Single pinned QGS training on the staged A03 trial root: full resolution,
# every-8th view held out, one seed, checkpoints at 7k (pre-reg onset, the
# causal test is free) and 30k. Staging (symlinks + alpha-preserving byte
# copies) runs first and refuses loudly on wrong counts or missing alpha.
#
# Usage: sbatch slurm/qgs_train_a03.slurm
set -euo pipefail

STATUS_DIR="/data/gpfs/projects/punim2657/PGSR/logs"
trap 'echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $?" >> "$STATUS_DIR/job_status.log"' EXIT

QGS_PIN=74d05c945e99fcaef7afe5a8831903be71ad9b55
PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
QGS_REPO=$PGSR_ROOT/qgs_trial/repo
TRIAL_DATA=$PGSR_ROOT/qgs_trial/data_A03
OUT_DIR=$PGSR_ROOT/output/QGS_A03
ENV_PREFIX=$PGSR_ROOT/envs/qgs

echo "=== QGS training on A03 started $(date) on $(hostname) ==="
nvidia-smi | head -15 || true

module purge
module load GCC/11.3.0 OpenMPI/4.1.4
module load CUDA/11.8.0
module load Miniforge3/24.7.1-2
export CUDA_HOME="${EBROOTCUDA:?}"
export LD_LIBRARY_PATH="$CUDA_HOME/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"

eval "$(conda shell.bash hook)"
# MKL activate.d references unset vars under `set -u` (build job: `MKL_INTERFACE_LAYER:
# unbound variable`) -- relax nounset for the activation only, then restore.
set +u
conda activate "$ENV_PREFIX"
set -u

HAVE=$(git -C "$QGS_REPO" rev-parse HEAD)
[[ "$HAVE" == "$QGS_PIN" ]] || { echo "checkout at $HAVE, want $QGS_PIN -- refusing" >&2; exit 1; }

# Enter PGSR-side tooling without moving the QGS checkout:
# fetch this repo's main, take only slurm/ + scripts/.
git -C "$QGS_REPO" rev-parse --is-inside-work-tree >/dev/null  # sanity
PGSR_CHECKOUT=$PGSR_ROOT/repo
git -C "$PGSR_CHECKOUT" fetch origin main
git -C "$PGSR_CHECKOUT" checkout origin/main -- slurm scripts
DRIVER=$PGSR_CHECKOUT/scripts/qgs_run_train.py
STAGE=$PGSR_CHECKOUT/scripts/qgs_stage_a03.py
CONF=$PGSR_CHECKOUT/slurm/qgs_a03.yaml

"$ENV_PREFIX/bin/python" "$STAGE" "$PGSR_ROOT/data/17062025/A03" "$TRIAL_DATA"

if [[ -d "$OUT_DIR/point_cloud/iteration_30000" ]]; then
    echo "$OUT_DIR already holds a finished 30k run -- refusing." >&2; exit 1
fi
mkdir -p "$OUT_DIR"
cd "$QGS_REPO"

"$ENV_PREFIX/bin/python" "$DRIVER" --qgs_repo "$QGS_REPO" --conf "$CONF"

echo
echo "=== point clouds produced ==="
find "$OUT_DIR" -name 'iteration_*' -newermt '-1 day' | sort | tail -4
echo "=== QGS training on A03 finished $(date) ==="
echo "Verdict checkpoint: render held-out views at 7k vs 30k (dB) BEFORE fusing."
echo "Next: slurm/qgs_extract_a03.slurm (same voxel, masked fusion)."
