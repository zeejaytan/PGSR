#!/bin/bash
#SBATCH --job-name=pgsr-cov06
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_cov06_%j.log

# Ticket 06 audit 2b (gaussian coverage follow-up): 3-sigma box cover per arm
# + nearest-centre distances. CPU-only. mm labels provisional.
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
OUT_ROOT=$PGSR_ROOT/work/edge_06/cover

echo "=== PGSR 06 gauss-cover audit started $(date) on $(hostname) ==="

module purge
module load Miniforge3/24.7.1-2

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

mkdir -p "$OUT_ROOT"
cd "$REPO_DIR"
export PGSR_ROOT
"$ENV_PREFIX/bin/python" scripts/diag_gausscover_06.py "$OUT_ROOT"

echo "=== outputs ==="
ls -la "$OUT_ROOT"
echo "=== finished $(date) ==="
