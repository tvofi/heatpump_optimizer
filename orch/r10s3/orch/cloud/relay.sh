#!/bin/bash
# relay.sh <pr> <nonce>: fetch probe/rev-<pr>-<nonce8>, publish via local bus.sh push-verdict (dispatch record is here), print the review ref.
set -euo pipefail
pr=$1 n=$2 R=/Users/timmalmstrom/heatpump_optimizer d=$(mktemp -d)
git -C "$R" fetch -q origin "refs/heads/probe/rev-$pr-${n:0:8}"
git -C "$R" archive FETCH_HEAD | tar -x -C "$d"
grep -q "^bus-nonce: $n$" "$d/verdict.md" || { echo "nonce mismatch" >&2; exit 2; }
cp "$d/verdict.md" "$d/ev/verdict.orig"
sed -i "" -E "1s/^(Fix review: blocked [0-9a-f]{40}) \\[(.*)\\]$/\\1 \\2/" "$d/verdict.md"
python3 - "$d/verdict.md" <<'PY'
import re,sys
p=sys.argv[1]; L=open(p).read().split("\n")
m=re.fullmatch(r"(Fix review: merge [0-9a-f]{40}) \[(.*)\]", L[0])
if m:
    L[0]=m.group(1); L.insert(1,""); L.insert(2,"Reviewer note (moved off the first line by the orchestrator relay; original in ev/verdict.orig): "+m.group(2))
    open(p,"w").write("\n".join(L))
PY
h=$(head -1 "$d/verdict.md" | grep -oE "[0-9a-f]{40}")
grep -rqs "$h" "$d/ev" || { echo "REFUSE: no reviewer evidence file names head $h; return to the same reviewer" >&2; exit 3; }
cd "$R" && bash tools/audit/seat/bus.sh push-verdict "$pr" "$d/verdict.md" "$d/ev"
