#!/bin/bash
# Negative control: delete the six added production lines, run the self-test,
# show the FAIL lines, restore, verify the tree is clean and the blob matches.
set -u
WT="$HOME/hpo-seats/r10s6/review-2889/wt"
F="$WT/tools/audit/seat/roster_sync.py"
cd "$WT" || exit 1
head_blob=$(git rev-parse HEAD:tools/audit/seat/roster_sync.py)
trap 'git -C "$WT" checkout -- tools/audit/seat/roster_sync.py 2>/dev/null' EXIT
python3 -I - "$F" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
block = '''                    held = carried_from(g.get("carry") or [], pr.number)
                    if held is not None:
                        refusals.append((pr.number, dest,
                                         "already carried from "
                                         f"#{pr.number}: {held[:60]!r}"))
                        continue
'''
assert s.count(block) == 1, s.count(block)
open(p, "w").write(s.replace(block, ""))
print("MUTANT: removed the carried_from lookup and its refusal block (6 lines)")
PY
echo "--- self-test at the mutant ---"
timeout 300 python3 tools/audit/seat/roster_sync.py --self-test 2>&1 | grep -E "^FAIL|self-test:"
git -C "$WT" checkout -- tools/audit/seat/roster_sync.py
trap - EXIT
echo "--- after restore ---"
echo "status: $(git -C "$WT" status --porcelain | wc -l | tr -d ' ') dirty path(s)"
echo "head blob:      $head_blob"
echo "restored blob:  $(git -C "$WT" rev-parse HEAD:tools/audit/seat/roster_sync.py)"
echo "self-test at the restored head:"
timeout 300 python3 tools/audit/seat/roster_sync.py --self-test 2>&1 | tail -1
