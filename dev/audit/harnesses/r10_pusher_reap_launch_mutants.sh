#!/usr/bin/env bash
# R10-PUSHER-REAP (#2524): every production launch the fix makes asynchronous,
# and every lead it names, against the self-tests that are meant to pin it.
# Each mutant is one exact-once text replacement (or a few, applied together)
# in a fresh detached worktree at <rev>; the worktree is removed afterwards.
# A mutant whose every named self-test still prints 0 failed is a launch line
# no arm exercises -- the class #2524's round-4 review found at cloud_relay.sh's
# production update branch (only the HPO_RELAY_UPDATE stub branch was run).
#
#   bash dev/audit/harnesses/r10_pusher_reap_launch_mutants.sh <rev> [MUTANT...]
#
# With no MUTANT every row below runs, M0 (no change) first. Each self-test runs
# under `timeout ${MUT_TIMEOUT:-900}`; a foreground mutant can hold a stop arm
# until then, which prints rc=124 and the arms failed so far.
set -uo pipefail
rev=${1:?usage: r10_pusher_reap_launch_mutants.sh <rev> [MUTANT...]}; shift
top=$(git rev-parse --show-toplevel) || exit 2

CR='bash tools/audit/seat/cloud_relay.sh --self-test'
TR='bash tools/audit/seat/train.sh --self-test'
PA='bash tools/audit/seat/pr_args.sh --self-test'
AP='bash tools/pr/app_push.sh --self-test'
MT='python3 tools/audit/seat/merge_train.py --self-test'

# row <id> <self-tests, ;-separated> [<file> <anchor> <replacement> [<anchor> <replacement>...]]
ROWS=()
row() { local IFS=$'\x1f'; ROWS+=("$*"); }
row M0 'CR;TR;PA;AP;MT'
# cloud_relay.sh's update launch: one line for the stub and the production route
row CR-FG CR tools/audit/seat/cloud_relay.sh '"${upd[@]}" "$br" "$hs" "$body" $iss >&2 &' '"${upd[@]}" "$br" "$hs" "$body" $iss >&2'
# the same with $! still bound (a trivial job after it): the foreground mutant above
# also unbinds $! under set -u, which ends the relay before any stop arm can judge it
row CR-FG-BOUND CR tools/audit/seat/cloud_relay.sh '"${upd[@]}" "$br" "$hs" "$body" $iss >&2 &' '"${upd[@]}" "$br" "$hs" "$body" $iss >&2; : &'
row CR-LEADNAME CR tools/audit/seat/cloud_relay.sh 'PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD" || urc=$?' 'crl=$!; wait "$crl" || urc=$?'
row CR-PRODPATH CR tools/audit/seat/cloud_relay.sh 'upd=(bash "$HERE/update_pr.sh")' 'upd=(bash "$HERE/update_pr.missing")'
# the review's two mutants of a01627177715's split launch (its production branch); they apply only there
row F-CR-ELSEFG CR tools/audit/seat/cloud_relay.sh 'else bash "$HERE/update_pr.sh" "$br" "$hs" "$body" $iss >&2 & fi' 'else bash "$HERE/update_pr.sh" "$br" "$hs" "$body" $iss >&2; fi'
row F-CR-ELSELEAD CR tools/audit/seat/cloud_relay.sh 'PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD" || urc=$?' 'u=$!; [ -z "${HPO_RELAY_UPDATE:-}" ] || PR_REAP_LEAD=$u; wait "$u" || urc=$?'
row TR-FG TR tools/audit/seat/train.sh ') >> "$log" 2>&1 &' ') >> "$log" 2>&1'
row TR-LEAD TR tools/audit/seat/train.sh 'PR_REAP_LEAD=$!' 'TRL=$!' 'wait "$PR_REAP_LEAD"' 'wait "$TRL"'
row TR-RC TR tools/audit/seat/train.sh 'rc=0; wait "$PR_REAP_LEAD" || rc=$?' 'rc=0; wait "$PR_REAP_LEAD" || :'
row OP-FG1 PA tools/audit/seat/open_pr.sh '> $D/p1.log 2>&1 &' '> $D/p1.log 2>&1'
row OP-FG2 PA tools/audit/seat/open_pr.sh '> $D/p2.log 2>&1 &' '> $D/p2.log 2>&1'
row UP-FG PA tools/audit/seat/update_pr.sh '> $WT.log 2>&1 &' '> $WT.log 2>&1'
row HP-FG PA tools/audit/seat/handoff_push.sh '> "$B.push.log" 2>&1 &' '> "$B.push.log" 2>&1'
row RM-FG PA tools/audit/seat/remerge_main.sh '> "$PL" 2>&1 &' '> "$PL" 2>&1'
row AP-FG AP tools/pr/app_push.sh '( cd "$wt" && bash "$prepr" "$body" "$@" ) & prepr_pid=$!' '( cd "$wt" && bash "$prepr" "$body" "$@" ) || prepr_rc=$?' \
  '    wait "$prepr_pid" || prepr_rc=$?' '    :'
row AP-PUSHFG AP tools/pr/app_push.sh '-c http.postBuffer=64m push "https://github.com/$repo.git" "$br" &' '-c http.postBuffer=64m push "https://github.com/$repo.git" "$br"'
# app_mint.sh's mint_token, unless told the caller owns the EXIT trap, replaces app_push's reap
row AP-MINTTRAP AP tools/pr/app_push.sh 'MINT_TRAP=caller  # the EXIT trap' '# MINT_TRAP=caller  # the EXIT trap'
# the tool's stop in Train._run (16-space indent: the self-test driver's own terminate() has 12)
row MT-KILL MT tools/audit/seat/merge_train.py '                p.terminate()' '                p.kill()'

mutate() { # <file> <anchor> <replacement> [...]: exact-once, or exit 3
  python3 -I - "$@" <<'PY'
import sys
p, pairs = sys.argv[1], sys.argv[2:]
s = open(p).read()
for a, b in zip(pairs[::2], pairs[1::2]):
    n = s.count(a)
    if n != 1:
        sys.exit("anchor occurs %d times in %s: %s" % (n, p, a))
    s = s.replace(a, b)
open(p, "w").write(s)
PY
}

for r in "${ROWS[@]}"; do
  IFS=$'\x1f' read -r -a parts <<< "$r"; id=${parts[0]}; tests=${parts[1]}
  if [ $# -gt 0 ]; then case " $* " in *" $id "*) ;; *) continue;; esac; fi
  wt=$(mktemp -d) || exit 2
  git -C "$top" worktree add -q --detach "$wt/t" "$rev" || exit 2
  if [ ${#parts[@]} -gt 2 ]; then
    ( cd "$wt/t" && mutate "${parts[@]:2}" ) || { echo "MUTANT $id: NOT APPLIED at $rev"; git -C "$top" worktree remove --force "$wt/t"; rm -rf "$wt"; continue; }
  fi
  IFS=';' read -r -a tl <<< "$tests"
  for k in "${tl[@]}"; do
    cmd=${!k}
    ( cd "$wt/t" && PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub timeout "${MUT_TIMEOUT:-900}" $cmd ) > "$wt/out" 2>&1; rc=$?
    sum=$(grep -E 'self-test: [0-9]+ checks|self-test: ok|self-test:' "$wt/out" | tail -1)
    echo "MUTANT $id: $k rc=$rc ${sum:-<no summary line>}"
    grep -E '^ *FAIL' "$wt/out" | sed 's/^ */    /' | cut -c1-200
  done
  git -C "$top" worktree remove --force "$wt/t"; rm -rf "$wt"
done
