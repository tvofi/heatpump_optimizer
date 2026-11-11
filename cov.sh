#!/bin/bash
# coverage term: mutant_run --diff, cap 40, report-only, at each candidate block head with the group self-test
until grep -q DONE /tmp/claude-0/sp/wall/summary.txt 2>/dev/null; do sleep 10; done
cd /root/wt; mkdir -p /tmp/claude-0/sp/cov
st() { printf "python3 -I %s --self-test && " "$@" | sed 's/ && $//'; }
run() { k=$1; shift; pr=${k%-*}; h8=${k#*-}; read p head base < <(awk -v p=$pr -v h=$h8 '$1==p && index($2,h)==1' /tmp/claude-0/sp/bases.txt)
  cmd="bash -c '$*'"; s=$(date +%s)
  python3 -I tools/audit/seat/mutant_run.py --diff "$base...$head" --cmd "$cmd" --max-mutants 40 --report-only > /tmp/claude-0/sp/cov/$k.out 2>&1; rc=$?
  echo "$k rc=$rc wall_s=$(( $(date +%s) - s )) survivors=$(grep -c ^SURVIVED /tmp/claude-0/sp/cov/$k.out) cmd=$*" >> /tmp/claude-0/sp/cov/summary.txt; }
run 3248-c8c50b9f "$(st tools/audit/seat/ledger.py tools/audit/seat/orchestrator_tick.py)"
run 3252-69aa9cd3 "$(st tools/audit/seat/orchestrator_tick.py)"
run 3260-2fa354bf "$(st tools/audit/carry_audit.py)"
run 3262-c95c3b4b "$(st tools/audit/seat/beat_jobs.py tools/audit/seat/outside_intake.py)"
run 3264-09ec9a88 "$(st tools/audit/seat/gantt_drift.py)"
run 3301-926a0149 "$(st tools/pr/ci_predict.py)"
run 3326-8f073db7 "$(st tools/audit/seat/handover_prompt.py tools/audit/seat/orchestrator_tick.py tools/audit/seat/resume_doc.py tools/audit/seat/roster_lib.py tools/plan/replan.py)"
run 3337-d0db3e30 "$(st tools/audit/seat/roster_queue.py)"
run 3425-779c9432 "$(st tools/audit/seat/orchestrator_tick.py tools/audit/seat/owed_unactioned.py)"
run 3427-7cbfa680 "$(st tools/audit/seat/gh_calls.py tools/ci/codescan_wait.py)"
run 3232-6e048afc "env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py \"R.section(\\\"worker read timeout\""
echo DONE >> /tmp/claude-0/sp/cov/summary.txt
