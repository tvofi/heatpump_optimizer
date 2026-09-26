#!/usr/bin/env bash
# D14 sweep, class "a sign floor on a price margin breaks the stated piecewise identity".
# Finding: D2-s3-02 (weakened(low) -- pv.import_margin floors at 0 when export_price > import
# price; blended_block_prices' "effective = prices - margin*covered_fraction" piecewise
# construction then silently degrades to "effective = prices" (no PV credit at all) instead of
# the signed identity its own docstring assumes.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
grep -n "import_margin\|np\.clip.*0\.0, None)" custom_components/heatpump_optimizer/pv.py custom_components/heatpump_optimizer/optimizer.py
