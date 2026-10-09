#!/bin/bash
. /Users/timmalmstrom/hpo-seats/review-2067/evidence/pgq.sh
cd /Users/timmalmstrom/hpo-seats/review-2067/wt
FILES="tools/pr/prepr.sh .claude/hooks/session-start.sh .claude/hooks/stop-selfcheck.sh .claude/hooks/pre-edit.sh tools/pr/approve_held_runs.sh tools/audit/worktree_gc.sh"
M=$(mktemp -d); for f in $FILES; do mkdir -p "$M/$(dirname $f)"; git show d8c34eeb:$f > "$M/$f"; done
cd "$M"; pipe_grep_q_sites $FILES; echo "RESULT classrow at-d8c34eeb-files rc=$? (want 1)"; rm -rf "$M"
