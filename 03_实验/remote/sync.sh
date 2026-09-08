#!/usr/bin/env bash
# Synchronize this workspace with the configured AutoDL host from macOS/Linux.
set -euo pipefail

usage() {
  printf 'Usage: %s {push|pull|status|check|shell}\n' "${0##*/}" >&2
  exit 2
}

action=${1:-}
[[ $# -eq 1 ]] || usage

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd "$script_dir/../.." && pwd)
remote_host=${REMOTE_HOST:-autodl}
remote_dir=${REMOTE_DIR:-/root/autodl-tmp}

case "$action" in
  push)
    ssh "$remote_host" "mkdir -p $remote_dir/code $remote_dir/logs $remote_dir/results"
    rsync -av --include='*.sh' --exclude='*' "$script_dir/" "$remote_host:$remote_dir/"
    rsync -av --include='*.py' --exclude='*' "$script_dir/" "$remote_host:$remote_dir/code/"
    if [[ -d "$repo_root/03_实验/code" ]]; then
      rsync -av --exclude='__pycache__/' --exclude='*.pyc' \
        "$repo_root/03_实验/code/" "$remote_host:$remote_dir/code/"
    fi
    ssh "$remote_host" "find $remote_dir/code -maxdepth 2 -type f -print | sort"
    ;;
  pull)
    mkdir -p "$repo_root/03_实验/results" "$repo_root/03_实验/logs"
    rsync -av "$remote_host:$remote_dir/results/" "$repo_root/03_实验/results/"
    rsync -av "$remote_host:$remote_dir/logs/" "$repo_root/03_实验/logs/"
    ;;
  status)
    ssh "$remote_host" "nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv; echo; echo '--- tmux ---'; tmux ls 2>/dev/null || echo no_tmux_sessions; echo; echo '--- disk ---'; df -h $remote_dir | tail -1; echo; echo '--- results ---'; ls -la $remote_dir/results"
    ;;
  check)
    ssh "$remote_host" "bash $remote_dir/check_env.sh"
    ;;
  shell)
    exec ssh "$remote_host"
    ;;
  *)
    usage
    ;;
esac
