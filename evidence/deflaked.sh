#!/bin/bash
# Reviewer's harness wrapper: neutralise only the self-test EXIT trap's rm -rf "$W"
# (which killed pre-exec ZPID-loop subshells run, deleting the fixture), then run the self-test.
set -e
f=tools/audit/worktree_gc.sh
sed -i "119s/rm -rf \"\\\$W\"' EXIT\$/:' EXIT/" "$f"
sed -n 119p "$f" | grep -q ":' EXIT\$" || { echo "deflake sed missed line 119"; exit 9; }
exec bash "$f" --self-test
