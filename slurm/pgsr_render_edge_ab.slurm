#!/bin/bash
#SBATCH --job-name=pgsr-render-edge-ab
#SBATCH --account=punim2657
#SBATCH --partition=cascade
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/PGSR/logs/pgsr_render_edge_ab_%j.log

# First-look renders + relief stats for BOTH lama-face-fill trial arms.
# Runs scripts/measure_edge_baseline.py (matplotlib Agg, trimesh, scipy --
# CPU-only, no GPU) on each arm's fused post mesh. Outputs per arm:
# stats.json, relief_hist.png, closeup_0/1.png, context.png -- small files
# for the laptop landing zone; the 264/302M meshes stay on Spartan.
#
# SCALE ASSUMPTION (explicit, ticket 04 must provenance it): the script's
# MM_PER_UNIT=373.733 comes from the A03 route sidecar (blue base top face).
# A31 reuses the same 17062025 capture poses, so scene units should match --
# but axis labels stay provisional until 04 attaches scale provenance.
# These renders are for inspection (did fusion produce sane geometry?),
# not for scoring.
set -euo pipefail

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
REPO_DIR=$PGSR_ROOT/repo
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
OUT_ROOT=$PGSR_ROOT/work/edge_AB

echo "=== PGSR A/B first-look render started $(date) on $(hostname) ==="

module purge
module load Miniforge3/24.7.1-2

eval "$(conda shell.bash hook)"
conda activate "$ENV_PREFIX"

cd "$REPO_DIR"
PY="$ENV_PREFIX/bin/python"

for spec in "A_lama:A31A_lama" "B_ctrl:A31B_ctrl"; do
    arm="${spec%%:*}"
    model="${spec##*:}"
    mesh="$PGSR_ROOT/output/$model/mesh/tsdf_fusion_post.ply"
    outdir="$OUT_ROOT/$arm"
    [[ -f "$mesh" ]] || { echo "missing fused mesh $mesh" >&2; exit 1; }
    echo "--- arm $arm: $mesh -> $outdir ---"
    "$PY" scripts/measure_edge_baseline.py "$mesh" "$outdir"
done

echo "=== outputs ==="
ls -la "$OUT_ROOT/A_lama" "$OUT_ROOT/B_ctrl"
echo "=== first-look render finished $(date) ==="
echo "Next: fetch the small PNGs/JSON to the laptop and look at them before any scoring."
