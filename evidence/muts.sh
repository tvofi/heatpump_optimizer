#!/usr/bin/env bash
# base, then each mutant on pump_arbiter.py, restored after each.
set -u
W=/Users/timmalmstrom/hpo-seats/r10s6/rev-3866-delta
S=/Users/timmalmstrom/hpo-seats/r10s6/rev-3866-delta-scratch
P=$W/custom_components/heatpump_optimizer/pump_arbiter.py
cd $W
bash $S/drive.sh base
mut() {
  name=$1; shift
  python3 - "$P" "$@" <<'EOF'
import sys
p, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(p).read()
assert t.count(old) == 1, (old, t.count(old))
open(p, "w").write(t.replace(old, new))
EOF
  echo "== $name applied: $(git diff --stat | tail -1)"
  bash $S/drive.sh "$name"
  git checkout -- custom_components
}
# M1103: the edge check's target (CMP_BOUND, closed -> open)
mut M1103 "if v is not None and v >= lowest]" "if v is not None and v > lowest]"
# MCAP: the one remaining boost cap at _map_inputs dropped -> the FLOWCAP block must catch it
mut MCAP "_space_limit_c(inp) or math.inf)" "math.inf)"
# MRESTORE: re-adding the deleted guard (the round-1 finding's lines) -> no check moves (equivalence null)
mut MRESTORE "        caps.append(ceiling)
    return min(caps)" "        caps.append(ceiling)
    if (limit := _space_limit_c(inp)) is not None:
        caps.append(limit)
    return min(caps)"
git status --short | head
