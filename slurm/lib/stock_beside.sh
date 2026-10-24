# stock_beside.sh -- unpack the pinned stock PGSR commit beside the tooling, and record it.
#
# A PGSR run uses two commits: stock upstream code (zju3dv/PGSR, never edited) and this
# fork's tooling (slurm/, scripts/). Until 2026-10-24 both came from one Spartan tree whose
# HEAD said stock and whose slurm/ and scripts/ had been checked out from main on top, so
# no run could say which tooling it used. Now each run unpacks both, and records both.
#
# Source it right after run_from_commit.sh, which has unpacked the tooling commit at $SRC:
#
#   source /data/gpfs/projects/punim2657/agent/pr-workspace/scripts/run_from_commit.sh \
#       "$CANONICAL" "$SOURCE_COMMIT" "$RUN_DIR"
#   source "$SRC/slurm/lib/stock_beside.sh"
#   cd "$STOCK"                                  # stock code at exactly the pin
#   python train.py ...                          # stock entry points
#   python "$SRC/scripts/mesh_stats.py" ...      # our tooling, from the tooling commit
#
# The pin is $SRC/slurm/stock_pin.txt, so the tooling commit alone names both, and the run's
# directory name (which carries the tooling commit) determines the whole run. The stock commit
# must be on a remote branch of the canonical checkout: our origin/main descends from it, so
# `git fetch origin` is enough. The same refusal run_from_commit.sh applies. Exports STOCK and STOCK_COMMIT, appends
# stock_* lines to $RUN_DIR/source.txt, and deletes both trees when the job exits.

stock_beside_fail() { echo "stock_beside: $*" >&2; return 1; }

stock_beside_cleanup() {
    case "${STOCK:-}" in
        */rfc-stock-*) [ -d "$STOCK" ] && rm -rf -- "$STOCK" ;;
    esac
    run_from_commit_cleanup
}

stock_beside() {
    local pin_file="$SRC/slurm/stock_pin.txt" pin sha branches
    [ -n "${SRC:-}" ] && [ -n "${RUN_DIR:-}" ] && [ -n "${CANONICAL:-}" ] \
        || { stock_beside_fail "source run_from_commit.sh first (SRC, RUN_DIR, CANONICAL unset)"; return 1; }
    [ -f "$pin_file" ] || { stock_beside_fail "no $pin_file in tooling commit ${SOURCE_COMMIT:-?}"; return 1; }
    pin=$(tr -d '[:space:]' < "$pin_file")

    sha=$(git -C "$CANONICAL" rev-parse --verify --quiet "${pin}^{commit}") \
        || { stock_beside_fail "stock pin $pin is not in $CANONICAL; git -C $CANONICAL fetch origin"; return 1; }
    branches=$(git -C "$CANONICAL" branch -r --contains "$sha" --format='%(refname)' \
        | grep -v '/HEAD$' | sed 's#^refs/remotes/##' | tr '\n' ' ')
    [ -n "$branches" ] || { stock_beside_fail "stock pin $sha is on no remote branch of $CANONICAL"; return 1; }

    STOCK=$(mktemp -d "${TMPDIR:-/tmp}/rfc-stock-${SLURM_JOB_ID:-$$}-XXXX") \
        || { stock_beside_fail "cannot make a directory under ${TMPDIR:-/tmp}"; return 1; }
    trap stock_beside_cleanup EXIT
    git -C "$CANONICAL" archive --format=tar "$sha" | tar -x -C "$STOCK" \
        || { stock_beside_fail "git archive of $sha failed"; return 1; }

    STOCK_COMMIT="$sha"
    export STOCK STOCK_COMMIT
    {
        echo "stock_commit=$sha"
        echo "stock_branches=${branches% }"
        echo "stock_pin_file=slurm/stock_pin.txt@${SOURCE_COMMIT:-}"
    } >> "$RUN_DIR/source.txt"
    echo "stock_beside: stock $sha unpacked at $STOCK, tooling ${SOURCE_COMMIT:-?} at $SRC"
}

stock_beside || case $- in *i*) return 1 ;; *) exit 1 ;; esac
