#!/usr/bin/env bash
# D14 sweep, class "persistent failure swallowed at DEBUG".
# Finding: D1-s2-04 (verified, medium -- 24 total except-Exception-then-_LOGGER.debug guards in
# coordinator.py; the finder's own harness (tools/audit/round9/D1/s2/guards.py) injects a
# persistent exception into each of the 5 guards reachable on the live optimization cycle and
# drives 3 consecutive cycles, finding 0 visible records (WARNING+/issue) at every one --
# silent_sites=5 of 5).
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
echo "--- static seam list: every except-Exception -> _LOGGER.debug guard ---"
grep -n -A2 'except Exception' custom_components/heatpump_optimizer/coordinator.py | grep "_LOGGER.debug"
echo "--- dynamic: the 5 cycle-path guards, injected + driven for 3 cycles (existing D1 harness) ---"
echo "harness: tools/audit/round9/D1/s2/guards.py"
