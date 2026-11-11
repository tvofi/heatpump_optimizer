#!/bin/bash
# R10-TRAIN-RAISE-HOLD (#2401): the mutation drive for Train.raise_hold, the
# one reading of a budget raise merge_train.py's approve and
# queue_pre_flight.py share. Each mutant removes one predicate of the fix,
# runs both self-tests, restores the files, and prints each self-test's last
# line and its FAIL lines: a killed mutant prints failures, a survivor
# "0 failed" twice. P1 is the defect itself (the path decides); Q1 is
# pre-flight's own. The CI mutation lane does not cover these files: its
# scope is production code, and nothing under tools/ is in it.
# Run from a clean checkout of the branch, all mutants or the ones named:
#   bash dev/audit/harnesses/r10_train_raise_hold_mutants.sh [M0 P1 Q1 ...]
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
T=tools/audit/seat/merge_train.py; Q=tools/audit/seat/queue_pre_flight.py
RP=dev/audit/harnesses/r10_train_raise_hold_replay.py
git diff --quiet -- "$T" "$Q" "$RP" || { echo "$T or $Q has uncommitted edits; the restore would erase them"; exit 2; }
want=" $* "
tests() {
  for f in "$T" "$Q"; do
    out=$(python3 "$f" --self-test 2>&1)
    echo "   $(echo "$out" | tail -1)"; echo "$out" | grep FAIL | sed 's/^/     /'
  done
}
rtests() { # the replay's own self-test: a failing read prints a Stop, never a hold
  out=$(python3 "$RP" --self-test 2>&1)
  echo "   $(echo "$out" | tail -1)"; echo "$out" | grep FAIL | sed 's/^/     /'
}
mutr() { # name, python replace old->new in the replay
  name=$1; old=$2; new=$3
  [ "$want" = "  " ] || [[ "$want" == *" $name "* ]] || return 0
  python3 - "$RP" "$old" "$new" 2>/dev/null <<'P' || { echo "== $name: PATTERN NOT FOUND"; return; }
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1; open(p,'w').write(s.replace(o,n))
P
  echo "== $name"; rtests; git checkout -q -- "$RP"
}
mut() { # name, file, python replace old->new
  name=$1; file=$2; old=$3; new=$4
  [ "$want" = "  " ] || [[ "$want" == *" $name "* ]] || return 0
  python3 - "$file" "$old" "$new" 2>/dev/null <<'P' || { echo "== $name: PATTERN NOT FOUND"; return; }
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1; open(p,'w').write(s.replace(o,n))
P
  echo "== $name"; tests; git checkout -q -- "$T" "$Q"
}
if [ "$want" = "  " ] || [[ "$want" == *" M0 "* ]]; then echo "== M0 baseline"; tests; rtests; fi
mut P1 "$T" '            _paths, raises = g.raises_between(base, h, ls, show)' \
  '            _paths, raises = g.raises_between(base, h, ls, show); raises = raises or [f for f in files if f.endswith(g.SUFFIX)]'
mut J1 "$T" ',
                                 justify=lambda: g.justification(self._body(pr)))' ')'
mut W1 "$T" '                raise Stop("approve", f"code-owned and {why}")' \
  '                raise Stop("approve", "code-owned and a budget file changed: a raise is the owner'"'"'s (0013)")'
mut H1 "$T" '            if held:
                self.log(f"#{pr} the owner'"'"'s approval is at the head: {why}")' '            if False:
                self.log(f"#{pr} the owner'"'"'s approval is at the head: {why}")'
mut U1 "$T" '        if unseen:' '        if False:'
mut R1 "$T" '            if code:
                raise Stop("approve", f"the budget read failed (' '            if False:
                raise Stop("approve", f"the budget read failed ('
mut T1 "$T" '                                 lambda _r, cid, c, t: g.mandate_state(cid, c, t, now, at, "merge"),' \
  '                                 None,'
mut B1 "$T" '        trees: dict[str, set[str]] = {}' '        self._body(pr)
        trees: dict[str, set[str]] = {}'
mut Q1 "$Q" '        if not held:
            return "PARK", "approve", why' '        if False:
            return "PARK", "approve", why'
# The replay (the body's live control) fails closed: S1 reads a failed command's
# text as its value (the defect the verdict on #2421 found), S2 drops the
# 40-hex test on the head and the base.
mutr S1 '    if rc != 0:
        raise ReadFailed' '    if False:
        raise ReadFailed'
mutr S2 '    if not mt.is_sha(v):' '    if False:'
