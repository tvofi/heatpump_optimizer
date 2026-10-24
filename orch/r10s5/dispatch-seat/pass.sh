#!/bin/bash
# One dispatch-seat pass: touch alive, diff review/* and handoff refs against the previous pass, show the queue.
D=/Users/timmalmstrom/hpo-orch/r10s5/dispatch-seat; R=/Users/timmalmstrom/hpo-orch/r10s5
cd /Users/timmalmstrom/hpo-seats/r10s5/orch-wt || exit 1
touch $R/dispatch.alive; date -u +%FT%H:%M:%SZ
git ls-remote origin 'refs/heads/review/*' > $D/review.now || { echo "LS-REMOTE FAILED"; exit 1; }
echo "-- review moved:"; comm -13 <(sort $D/review.prev) <(sort $D/review.now) | while read sha ref; do
  git fetch -q origin "$ref"; n=${ref##*/}
  echo "$sha $ref | $(git log -1 --format=%s FETCH_HEAD) | live: $(gh pr view $n -R tvofi/heatpump_optimizer --json headRefOid,state -q '.headRefOid+" "+.state')"
done
git ls-remote origin 'refs/heads/handoff/*' 'refs/heads/handoff-body/*' > $D/handoff.now || exit 1
echo "-- handoff moved (roster branch excluded):"; comm -13 <(sort $D/handoff.prev) <(sort $D/handoff.now) | grep -Ev 'handoff/audit-r10-(roster|plan)$'
[ ! -f $D/wc.seen ] && grep -Eq '^([0-9TZ:-]+ )?([a-z0-9 -]+: )?WINDOW-CLOSED' $R/to-main.txt && { touch $D/wc.seen; echo "WINDOW-CLOSED seen"; }
[ ! -f $D/reopen.seen ] && [ "$(gh pr view 2675 -R tvofi/heatpump_optimizer --json state -q .state)" = OPEN ] && { touch $D/reopen.seen; echo "REOPENED #2675 seen"; }
[ ! -f $D/msh.seen ] && grep 'R10-MERGE-SUBJECT-HARDEN' $R/roster-report.txt | grep -qE 'pushed|read back' && { touch $D/msh.seen; echo "ROSTER R10-MERGE-SUBJECT-HARDEN: $(grep 'R10-MERGE-SUBJECT-HARDEN' $R/roster-report.txt | tail -2)"; }
echo "-- queue new:"; comm -13 <(sort $D/queue.done) <(grep -v '^#' $R/dispatch-queue.txt | sort)
echo "-- to-main OWED open PR:"; grep 'OWED: open PR' $R/to-main.txt | tail -2
echo "-- watched:"; grep -E 'handoff/(r10-ci-layout-p2b-v2|r10-orch-ledger)$' $D/handoff.now
cp $D/review.now $D/review.prev; cp $D/handoff.now $D/handoff.prev
