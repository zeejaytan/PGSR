#!/bin/bash
#SBATCH --job-name=pgsr-gauss06
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_gauss06_%j.log

# Ticket 06 audit 2 (gaussian): count trained Gaussians in the sherd box per
# arm + footprint stats. CPU-only (numpy + matplotlib Agg). mm provisional.
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
OUT_ROOT=$PGSR_ROOT/work/edge_06/gauss

echo "=== PGSR 06 gaussian audit started $(date) on $(hostname) ==="

module purge
module load Miniforge3/24.7.1-2

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

mkdir -p "$OUT_ROOT"
cd "$REPO_DIR"
export PGSR_ROOT
"$ENV_PREFIX/bin/python" scripts/diag_gauss_06.py "$OUT_ROOT"

echo "=== outputs ==="
ls -la "$OUT_ROOT"
echo "=== finished $(date) ==="
