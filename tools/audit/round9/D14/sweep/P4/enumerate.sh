#!/usr/bin/env bash
# D14 sweep, class P4: "The optimizer seed set or stop tolerance does not bracket the optimum".
# Finding: D0-s2-02 (verified, low -- the call-0 ladder gap on the 24h grid exceeds the flat-price
# null on shoulder prices: max 1.2012% vs 0.3247%, 8/16 cells over 0.1%).
# Heavy solver races (race.py's 80/64/32-cell grids) are NOT re-run here: minimal enumerator per
# the sweep brief for small classes. This lists the production call sites that feed a seed set
# into _multi_start_minimize -- the seam rule's structural half -- and reuses the finder's own
# REPORT.md grid as the positive control / disposition evidence instead of re-executing it.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
grep -n "_multi_start_minimize(\|def _price_ranked_start\|def _scoped_minimize" custom_components/heatpump_optimizer/optimizer.py
