cd "$1"; g=0; for i in $(seq 1 25); do l=$(bash tools/audit/worktree_gc.sh --self-test 2>/dev/null | tail -1); echo "$l"; case $l in *", 0 failed") g=$((g+1));; esac; done; echo "$g of 25 green"
