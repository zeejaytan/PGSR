#!/bin/bash
#SBATCH --job-name=pgsr-rea07
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_rea07_%j.log

# Ticket 07 reason test (cheap, CPU-only): SfM seed density at the face box
# vs neighbour boxes + Sobel energy face-core vs bbox vs rest of frame.
# mm labels provisional. No training, no fusion, no verdict.
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
OUT_ROOT=$PGSR_ROOT/work/edge_07/reason

echo "=== PGSR 07 reason test started $(date) on $(hostname) ==="

module purge
module load Miniforge3/24.7.1-2

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

mkdir -p "$OUT_ROOT"
cd "$REPO_DIR"
export PGSR_ROOT
"$ENV_PREFIX/bin/python" scripts/diag_reason_07.py "$OUT_ROOT"

echo "=== outputs ==="
ls -la "$OUT_ROOT"
echo "=== finished $(date) ==="
