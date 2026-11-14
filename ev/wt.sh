set -Eeo pipefail
hit=0; for i in $(seq 1 50); do if git worktree list --porcelain | grep -qxF "worktree $1"; then :; else hit=$((hit+1)); fi; done
echo "worktrees=$(git worktree list | wc -l) target=$1 false-negatives=$hit/50"
