#!/bin/bash
# wall time of mutant_run.py --diff (cap 40, report-only) over merged fixer diffs
cd /root/wt
run() { pr=$1; m=$2; cmd=$3
  s=$(date +%s.%N)
  python3 -I tools/audit/seat/mutant_run.py --diff "$m^1...$m^2" --cmd "$cmd" --max-mutants 40 --report-only > /tmp/claude-0/sp/wall/$pr.out 2>&1
  rc=$?; e=$(date +%s.%N)
  echo "$pr $m rc=$rc wall_s=$(echo "$e - $s" | bc) survivors=$(grep -c '^SURVIVED' /tmp/claude-0/sp/wall/$pr.out) cmd=$cmd" | tee -a /tmp/claude-0/sp/wall/summary.txt
}
run 3419 a7628041 "python3 -I tools/ci/selftest_scope.py --self-test"
run 3379 86953c6d "bash -c 'python3 -I tools/audit/seat/review_packet.py --self-test && python3 -I tools/audit/seat/cloud_dispatch.py --self-test'"
run 3384 c620ebba "bash -c 'python3 -I tools/audit/seat/orchestrator_tick.py --self-test && python3 -I tools/audit/seat/cloud_dispatch.py --self-test'"
run 3417 8efacee4 "bash -c 'python3 -I tools/audit/carry_audit.py --self-test && python3 -I tools/audit/seat/roster_edit.py --self-test && python3 -I tools/audit/seat/roster_lib.py --self-test && python3 -I tools/audit/seat/roster_sync.py --self-test && python3 -I tools/pr/ci_predict.py --self-test'"
run 3405 b421442e "env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py '# --- R10-WATER-SETPOINT-FEEDBACK (outside report'"
echo DONE >> /tmp/claude-0/sp/wall/summary.txt
