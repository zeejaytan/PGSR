#!/bin/bash
#SBATCH --job-name=pgsr-clu06
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=02:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_clu06_%j.log

# Ticket 06 audit 1 (cluster): re-run the stock post-filter on ONE arm's RAW
# mesh with keep 10 -> 25 -> all; render the sherd box per setting.
# CPU-only (open3d + matplotlib Agg). mm labels provisional.
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
OUT_ROOT=$PGSR_ROOT/work/edge_06/cluster
ARM="${1:-A_lama}"

echo "=== PGSR 06 cluster audit started $(date) on $(hostname), arm $ARM ==="

module purge
module load Miniforge3/24.7.1-2

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

mkdir -p "$OUT_ROOT"
cd "$REPO_DIR"
export PGSR_ROOT
"$ENV_PREFIX/bin/python" scripts/diag_cluster_06.py "$OUT_ROOT" "$ARM"

echo "=== outputs ==="
ls -la "$OUT_ROOT"
echo "=== finished $(date) ==="
