#!/bin/bash
#SBATCH --job-name=pgsr-render-edge-04
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_render_edge_04_%j.log

# Ticket 04 phase 1: locate the A31 sherd in 3D (ONE triangulation, shared
# 33-camera geometry) and render MATCHING sherd-scale close-ups for both arms.
# Runs scripts/locate_a31_render_04.py (matplotlib Agg, trimesh -- CPU-only).
# Outputs work/edge_04/: locate.json + per arm closeup_0/1.png, context.png.
#
# SCALE (explicit): mm axes/bars use the PROVISIONAL A03 373.733 mm/unit scale,
# unproven for A31. Inspection renders only; no scoring, no verdicts.
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
OUT_ROOT=$PGSR_ROOT/work/edge_04

echo "=== PGSR 04 sherd locate+render started $(date) on $(hostname) ==="

module purge
module load Miniforge3/24.7.1-2

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

mkdir -p "$OUT_ROOT"
cd "$REPO_DIR"
export PGSR_ROOT
"$ENV_PREFIX/bin/python" scripts/locate_a31_render_04.py "$OUT_ROOT"

echo "=== outputs ==="
ls -la "$OUT_ROOT" "$OUT_ROOT/A_lama" "$OUT_ROOT/B_ctrl"
echo "=== finished $(date) ==="
