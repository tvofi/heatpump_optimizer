set -o pipefail
python3 -I tools/audit/seat/orchestrator_tick.py --self-test | tee "$RUNNER_TEMP/ot-self-test.txt"
grep -Eq '^orchestrator_tick self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/ot-self-test.txt"

