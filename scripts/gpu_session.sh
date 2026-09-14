#!/usr/bin/env bash
# Hold a GPU allocation open and run commands inside it, without a queue wait each time.
#
# WHY. Building and debugging through `sbatch` turns every one-line fix into a queue wait
# plus a job startup, to learn one fact. The COLMAP build took seven submissions to get
# through solve -> configure -> compile -> link, and the waiting was most of the elapsed
# time; each failure itself took seconds. An allocation held open collapses that to the
# cost of the command.
#
# `sinteractive`/`srun --pty` need a terminal, which a non-interactive ssh does not have.
# So instead: submit a job that does nothing but sleep, then push commands into it with
# `srun --jobid=... --overlap`. Same node, same GPU, no queue between attempts.
#
# Workspace-wide helper: copy or symlink into any project that needs it.
#
# Default partition is gpu-a100-short: it grants far faster than the full
# partition and the default 4h hold fits its wall. For longer holds override
# explicitly: PARTITION=gpu-a100 ./scripts/gpu_session.sh start 8
#
# Usage (from the laptop or on Spartan):
#   ./scripts/gpu_session.sh start [hours]     # default 4
#   ./scripts/gpu_session.sh run  <command...>
#   ./scripts/gpu_session.sh shell             # print how to attach by hand
#   ./scripts/gpu_session.sh status
#   ./scripts/gpu_session.sh stop
#
# Reserve batch jobs for what they are good at: long production runs that nobody is
# waiting on. Use this for anything where the next step depends on what the last one said.
set -euo pipefail

STATE="${GPU_SESSION_STATE:-$HOME/.milo_gpu_session}"
LOG_DIR="${GPU_SESSION_LOG_DIR:-/data/gpfs/projects/punim2657/MILo/logs}"
PARTITION="${PARTITION:-gpu-a100-short}"
ACCOUNT="${ACCOUNT:-punim2657}"
CPUS="${CPUS:-16}"
MEM="${MEM:-128G}"

job_id() { [[ -f "$STATE" ]] && cat "$STATE" || true; }

job_state() {
    local id="$1"
    [[ -n "$id" ]] || { echo "NONE"; return; }
    squeue -j "$id" -h -o "%T" 2>/dev/null || echo "GONE"
}

case "${1:-status}" in

  start)
    HOURS="${2:-4}"
    ID=$(job_id)
    if [[ -n "$ID" && "$(job_state "$ID")" == "RUNNING" ]]; then
        echo "session $ID already running on $(squeue -j "$ID" -h -o '%N')"
        exit 0
    fi
    # A job whose only task is to wait. The real work arrives through srun --overlap.
    ID=$(sbatch --parsable \
        --job-name=gpu-session \
        --account="$ACCOUNT" --partition="$PARTITION" --gres=gpu:1 \
        --ntasks=1 --cpus-per-task="$CPUS" --mem="$MEM" \
        --time="${HOURS}:00:00" \
        --output="$LOG_DIR/gpu_session_%j.log" \
        --wrap="sleep ${HOURS}h")
    echo "$ID" > "$STATE"
    echo "submitted session $ID (${HOURS}h). Waiting for the grant..."
    # No cap: this command does not return until the node is yours, so a
    # background launch notifies on grant the same way slurm_poll.sh notifies
    # on finish. A grant nobody notices is how allocations idle — 6h burned
    # untouched Sep 2026 (30400952), then 1h43 more on its replacement, both
    # because the request went out with no watch attached.
    while [[ "$(job_state "$ID")" != "RUNNING" ]]; do
        echo "$(date '+%F %T') session $ID: $(job_state "$ID") -- still watching"
        sleep 60
    done
    echo "granted: session $ID on $(squeue -j "$ID" -h -o '%N')"
    printf '\a'
    if command -v powershell.exe >/dev/null 2>&1; then
        powershell.exe -c "New-BurntToastNotification -Text 'GPU session granted','$ID'" \
            >/dev/null 2>&1 || true
    fi
    ;;

  run)
    shift
    ID=$(job_id)
    [[ -n "$ID" ]] || { echo "No session. Run: $0 start" >&2; exit 1; }
    [[ "$(job_state "$ID")" == "RUNNING" ]] || {
        echo "Session $ID is $(job_state "$ID"), not RUNNING." >&2; exit 1; }
    # --overlap is required: the allocation's own step is the sleep, and without it srun
    # waits forever for resources that its own job already holds.
    # No --pty at all: srun is non-interactive by default, and "--pty=false" is rejected
    # ("must be numeric file descriptor") rather than treated as off.
    exec srun --jobid="$ID" --overlap bash -lc "$*"
    ;;

  shell)
    ID=$(job_id)
    echo "srun --jobid=$ID --overlap --pty bash -l"
    ;;

  status)
    ID=$(job_id)
    if [[ -z "$ID" ]]; then echo "no session recorded"; exit 0; fi
    echo "session $ID: $(job_state "$ID")"
    squeue -j "$ID" -o "%.10i %.12P %.8T %.10M %.10L %N" 2>/dev/null | tail -2
    ;;

  stop)
    ID=$(job_id)
    [[ -n "$ID" ]] && scancel "$ID" && echo "cancelled $ID"
    rm -f "$STATE"
    ;;

  *) echo "Usage: $0 {start [hours]|run <cmd>|shell|status|stop}" >&2; exit 1 ;;
esac
