#!/bin/bash
# Local stand-in (tvofi 2026-10-31: mechanical seat work goes into the sweep script). Tracked form owed:
# R10-ORCH-LEDGER carry "mechanical seats to beat jobs". Runs the sweep_template's mechanical steps and writes
# ONLY actionable lines to new.txt (+ new.stamp), which the orchestrator's single wake loop reads.
set -u
O=<STATE_DIR>; R=$O/s9/sweep-runner; W=<SEATS_DIR>/orch-wt2   # s10 2026-11-01: orch-wt froze at 2b6bef74 (10-31); its update_pr refused STALE CHECKOUT
export PATH=$W/tools/audit/seat/shims:$PATH HPO_STATE_DIR=$O
DRV=$O/s9/seat-opener/driver4.log; dl=$(wc -l < $DRV 2>/dev/null || echo 0)
n=0
emit(){ printf '%s\n' "$@" >> $R/new.tmp; }
while :; do
  n=$((n+1)); : > $R/new.tmp; cd $W || exit 1
  # NEVER move orch-wt here: tick_loop.sh / cloud_relay.sh / state_docs run from it and bash reads scripts incrementally (R10-FLY-RELAY-REVIEW-FF carry 5).
  # roster queue drain (retired roster seat): refusals and unrun lines only
  timeout 3700 python3 $R/roster_drain.py >> $R/new.tmp 2>&1
  # (1b) pulse: STOPPED / UNREADABLE only
  timeout 200 python3 -I tools/audit/seat/pulse.py --repo tvofi/heatpump_optimizer > $R/pulse.txt 2>&1
  grep -E 'STOPPED|UNREADABLE' $R/pulse.txt | grep -v 'bus.sh orphans printed no summary' | sed 's/^/PULSE: /' >> $R/new.tmp
  # (4e) cancel superseded runs; report only if it cancelled something or failed
  timeout 200 python3 -I tools/pr/cancel_superseded.py sweep --repo tvofi/heatpump_optimizer > $R/cancel.txt 2>&1 || emit "CANCEL-SWEEP failed: $(tail -1 $R/cancel.txt)"
  grep -q 'cancelled [1-9]' $R/cancel.txt && grep 'CANCEL-SWEEP' $R/cancel.txt >> $R/new.tmp
  # opener driver: new RESULT / REFUSE / ERROR lines since last pass
  if [ -f $DRV ]; then tl=$(wc -l < $DRV); [ "$tl" -gt "$dl" ] && sed -n "$((dl+1)),${tl}p" $DRV | grep -E 'RESULT|REFUSE|ERROR|NEEDS-TITLE|STUCK' | sed 's/^/OPENER: /' >> $R/new.tmp; dl=$tl; fi
  # (8) disk floor 15 GiB
  free=$(df -g /System/Volumes/Data | awk 'NR==2{print $4}'); [ "${free:-99}" -lt 15 ] && { emit "DISK: ${free} GiB free (<15); running worktree_gc"; bash tools/audit/worktree_gc.sh tvofi/heatpump_optimizer > $R/gc.txt 2>&1; }
  # every 2nd pass (~30 min): (4b) record beat and (5) owed_unactioned
  if [ $((n % 2)) -eq 1 ]; then
    git fetch -q origin handoff/audit-r10-roster 2>/dev/null
    timeout 300 python3 tools/plan/replan.py --out $O/s7/plan-live.json --slots 16 --seats 16 > $R/replan.txt 2>&1 || emit "REPLAN failed: $(tail -1 $R/replan.txt)"
    timeout 150 python3 tools/audit/seat/plan_page.py --plan $O/s7/plan-live.json --html $O/s7/plan-live.html > $R/plan_page.txt 2>&1 || emit "PLAN-PAGE failed: $(tail -1 $R/plan_page.txt)"
    grep -q "refused" $R/plan_page.txt && emit "PLAN-PAGE refused: $(grep -m1 refused $R/plan_page.txt | cut -c1-200)"
    cmp -s $O/s7/plan-live.html $O/plan.html || { cp $O/s7/plan-live.html $O/plan.html && emit "PLAN MOVED: plan.html re-rendered; republish owed (tvofi 11-06: every sweep updates the plan artifact)"; }
    # tvofi 2026-11-01: each plan render is compared against the Gantt baseline; every unacked slip is owed act|defer|accept
    G=$O/s10/gantt; git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json > $G/roster.json 2>/dev/null
    # 11-06: a handoff already in main is not work in flight; counting it hid the CP head R10-BODY-CONTRACT as busy for 28 h
    # a handoff is live only if its tip was committed in the last 12 h (merged-in or squashed handoffs keep old tips)
    git fetch -q origin '+refs/heads/handoff/*:refs/gantt/handoff/*' '+refs/heads/handoff-wip/*:refs/gantt/handoff-wip/*' 2>/dev/null
    cut=$(( $(date +%s) - 43200 ))
    git for-each-ref --format='%(objectname)%09%(refname)%09%(committerdate:unix)' refs/gantt/ | awk -F'\t' -v c=$cut '$3>=c {sub("refs/gantt/","refs/heads/",$2); print $1"\t"$2}' > $G/handoffs.txt
    # only fires from the last 12 h count as a live seat; an 11-05 fire line kept a finished group busy
    python3 -I -c 'import sys,re,datetime as d;c=d.datetime.now(d.timezone.utc)-d.timedelta(hours=12);[sys.stdout.write(l) for l in open(sys.argv[1]) if (m:=re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?)Z",l)) and d.datetime.fromisoformat(m[1]).replace(tzinfo=d.timezone.utc)>=c]' $O/s9/seat-dispatch/ledger-standin.txt > $G/fired-recent.txt 2>/dev/null
    gh pr list --repo tvofi/heatpump_optimizer --state open --limit 100 --json number,title > $G/prs.json 2>/dev/null
    timeout 120 python3 -I $R/gantt_drift.py --plan $O/s7/plan-live.json --baseline $G/baseline.json --acks $G/acks.txt --roster $G/roster.json --open-prs $G/prs.json --handoffs $G/handoffs.txt --fired $G/fired-recent.txt > $R/gantt.txt 2>&1 || emit "GANTT-DRIFT failed: $(tail -1 $R/gantt.txt)"
    grep -E '^GANTT-(SLIP|BASELINE)' $R/gantt.txt | sed 's/^/GANTT: /' >> $R/new.tmp
    # tvofi 11-06: the sweep's point is that no PR waits unheld; every open PR is mapped to its verdict and holder
    timeout 300 python3 -I $R/verdict_audit.py $O/s9/seat-dispatch/ledger-standin.txt "$HOME/.local/state/hpo/merge_train/*.log" $G/unheld-skip.txt > $R/unheld.txt 2>&1 || emit "VERDICT-AUDIT failed: $(tail -1 $R/unheld.txt)"
    grep '^UNHELD' $R/unheld.txt >> $R/new.tmp
    timeout 900 python3 -u tools/audit/seat/state_docs.py --push --mirror $O/state-mirror --plan $O/s7/plan-live.json > $R/state.txt 2>&1; src=$?; [ $src -ne 0 ] && emit "STATE-DOCS rc=$src (124 = timeout): $(grep -i -E 'refus|unavail|error' $R/state.txt | tail -1)"
    grep -h '^summary:' $R/replan.txt > $R/plan-summary.txt
    python3 -I tools/audit/seat/owed_unactioned.py --tick $O/tick.txt --state $O/owed-unactioned.json --acks $O/seat-ledger.md > $R/unact.txt 2>&1; rc=$?
    [ $rc -eq 1 ] && grep -E '^\s+-> |^\s+ack:' $R/unact.txt | sed 's/^ */UNACTIONED: /' >> $R/new.tmp
    [ $rc -eq 2 ] && emit "UNACTIONED-UNREADABLE: $(tail -1 $R/unact.txt)"
  fi
  if [ -s $R/new.tmp ]; then mv $R/new.tmp $R/new.txt; date -u +%FT%TZ > $R/new.stamp; else rm -f $R/new.tmp; fi
  echo "$(date -u +%FT%TZ) pass $n new=$( [ -f $R/new.stamp ] && cat $R/new.stamp || echo -) $(cat $R/plan-summary.txt 2>/dev/null | cut -c1-60)"
  sleep 900
done
