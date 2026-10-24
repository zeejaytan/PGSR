#!/bin/bash
#SBATCH --job-name=pgsr-2commit
#SBATCH --account=punim2657
#SBATCH --partition=sapphire,cascade
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:20:00

# Smoke test for the two-commit run (workbench-hygiene ticket 01): unpack the tooling commit
# and the pinned stock commit side by side, run one stock module and one tooling script, and
# leave both commits in $RUN_DIR/source.txt. Writes nothing outside the run directory.
#
# Submit from the login node through new_run.sh (AGENTS.md, Paths), never with plain sbatch:
#   MESH_DIRS="<dir> ..." optional; default the A03 fusion-masked mesh.
set -euo pipefail
: "${RUN_DIR:?submit through new_run.sh}" "${SOURCE_COMMIT:?}" "${CANONICAL:?}"

PGSR_ROOT=/data/gpfs/projects/punim2657/PGSR
ENV_PREFIX=/data/gpfs/projects/punim2657/MILo/envs/milo
MESH_DIRS="${MESH_DIRS:-$PGSR_ROOT/output/A03/mesh_A_masked}"

source /data/gpfs/projects/punim2657/agent/pr-workspace/scripts/run_from_commit.sh \
    "$CANONICAL" "$SOURCE_COMMIT" "$RUN_DIR"
source "$SRC/slurm/lib/stock_beside.sh"

module purge
module load Miniforge3/24.7.1-2
eval "$(conda shell.bash hook)"
set +u; conda activate "$ENV_PREFIX"; set -u
PY="$ENV_PREFIX/bin/python"

# Stock code runs from $STOCK and nowhere else: the tooling tree has the fork's comment in
# render.py, the stock tree must not.
[ -f "$STOCK/train.py" ] && [ -f "$STOCK/render.py" ] || { echo "stock tree incomplete" >&2; exit 1; }
if grep -q "Open3D integrate() takes world-to-camera" "$STOCK/render.py"; then
    echo "stock render.py carries the fork's comment: this is not the stock commit" >&2; exit 1
fi
[ ! -d "$STOCK/slurm" ] || { echo "stock tree has a slurm/ directory: wrong commit" >&2; exit 1; }
(cd "$STOCK" && "$PY" -c "import arguments; print('stock import ok:', arguments.__file__)") \
    | tee "$RUN_DIR/out/stock_import.txt"

# shellcheck disable=SC2086
if ls $MESH_DIRS >/dev/null 2>&1; then
    "$PY" "$SRC/scripts/mesh_stats.py" $MESH_DIRS | tee "$RUN_DIR/out/mesh_stats.txt"
else
    echo "no mesh at $MESH_DIRS; tooling checked by import instead" | tee "$RUN_DIR/out/mesh_stats.txt"
    "$PY" -c "import sys; sys.path.insert(0, '$SRC/scripts'); import mesh_stats; print('tooling import ok:', mesh_stats.__file__)" \
        | tee -a "$RUN_DIR/out/mesh_stats.txt"
fi

echo "=== source.txt ==="
cat "$RUN_DIR/source.txt"
