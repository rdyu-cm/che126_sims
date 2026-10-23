#!/usr/bin/env bash
# One run-progress update pass for the two-node cluster (decision D45, docs/decisions.md).
# Meant for cron on rdyu-server (every 10 min); each invocation does one pass and exits:
#   1. `sepsim progress --all` here (progress.md/.json and PNGs in each results/runs/<system>/<stage>/);
#   2. the same on the remote node over ssh (its own results/runs/);
#   3. rsync ONLY the remote progress.md, progress.json and progress_*.png into
#      results/progress/<remote>/<system>/<stage>/ (never over this node's files);
#   4. `sepsim progress --summary results/progress.md` over both trees (one table, node column).
# Cron safety: absolute paths, PATH with ~/.local/bin (uv), a flock so an overlapping run
# skips instead of piling up, a timeout on every step (a down remote cannot hang it), and
# its own log (logs/progress_update.log, cut to its last 2000 lines when it passes 1 MB).
# A failing step is logged and the pass goes on. The analyses run niced and
# single-threaded; finished holds are cached, so a pass is cheap.
#
# Parameters (environment variables):
#   SEPSIM_REMOTE             remote node (default rdyu-rog); empty to skip it
#   SEPSIM_REMOTE_PROJECT     project path on the remote (default: this project's path)
#   SEPSIM_REMOTE_UV          uv on the remote (default ~/.local/bin/uv)
#   SEPSIM_PROGRESS_TIMEOUT   seconds allowed per step (default 300)
#
# Options: -h|--help   print this header.
#
# Crontab line on rdyu-server (crontab -e; not installed by the repo):
#   */10 * * * * /home/rdyu/projects/che126_sims/scripts/progress_update.sh
# The remote must have the sepsim version with `progress` (ssubmit syncs the project).
set -uo pipefail

case "${1:-}" in
-h | --help)
    sed -n '2,/^set -uo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'
    exit 0
    ;;
"") ;;
*)
    echo "progress_update.sh: unknown option $1" >&2
    exit 2
    ;;
esac

export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
project="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
remote="${SEPSIM_REMOTE-rdyu-rog}"
remote_project="${SEPSIM_REMOTE_PROJECT:-$project}"
remote_uv="${SEPSIM_REMOTE_UV:-~/.local/bin/uv}"
limit="${SEPSIM_PROGRESS_TIMEOUT:-300}"
log="$project/logs/progress_update.log"

cd "$project" || exit 1
mkdir -p logs results/progress
if [[ -f "$log" && $(stat -c %s "$log") -gt 1048576 ]]; then
    tail -n 2000 "$log" >"$log.tmp" && mv "$log.tmp" "$log"
fi
exec >>"$log" 2>&1

exec 9>"$project/logs/.progress_update.lock"
if ! flock -n 9; then
    echo "[$(date '+%F %T')] previous pass still running; skipped"
    exit 0
fi

stamp() { date '+%F %T'; }
light=(timeout "$limit" nice -n 19)

echo "[$(stamp)] local: sepsim progress --all"
"${light[@]}" uv run --frozen sepsim progress --all >/dev/null ||
    echo "[$(stamp)] local pass had errors (exit $?)"
dirs=(--collect "$project/results/runs")
if [[ -n "$remote" ]]; then
    echo "[$(stamp)] $remote: sepsim progress --all"
    # shellcheck disable=SC2029  # expand the paths here, on purpose
    timeout "$limit" ssh -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=30 \
        "$remote" "cd '$remote_project' && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
        MKL_NUM_THREADS=1 nice -n 19 $remote_uv run --frozen sepsim progress --all >/dev/null"
    rc=$?
    if [[ $rc == 0 ]]; then
        mkdir -p "results/progress/$remote"
        timeout "$limit" rsync -a --prune-empty-dirs --timeout=60 \
            --include='*/' --include='progress.md' --include='progress.json' \
            --include='progress_*.png' --exclude='*' \
            "$remote:$remote_project/results/runs/" "$project/results/progress/$remote/" ||
            echo "[$(stamp)] rsync from $remote failed (exit $?)"
    else
        echo "[$(stamp)] $remote pass failed (exit $rc, 124 = timeout); the summary uses its last copied files"
    fi
    dirs+=(--collect "$project/results/progress/$remote")
fi
"${light[@]}" uv run --frozen sepsim progress --summary "$project/results/progress.md" \
    "${dirs[@]}" >/dev/null && echo "[$(stamp)] wrote results/progress.md"
