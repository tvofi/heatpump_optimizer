#!/usr/bin/env bash
# D14 sweep, class P8: "A currency or unit resolved by divergent precedence on different surfaces".
# Reuses the finder's own class enumerator (tools/audit/round9/D14/s2/p8_currency.py --seams,
# families A/B/C: feed->published unit, config-flow money widgets, card money surfaces) and adds
# family D: hard-coded SEK plausibility bounds compared against a value whose currency may not be SEK.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
echo "--- families A/B/C (money-figure currency resolution sites) ---"
PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/s2/p8_currency.py --seams
echo "--- family D (fixed-currency plausibility bound vs. a value of unknown currency) ---"
grep -n "IMPLAUSIBLE_FEE_SEK_PER_KWH" custom_components/heatpump_optimizer/*.py | grep -v "^.*://" | grep -E ":[0-9]+: *(IMPLAUSIBLE_FEE_SEK_PER_KWH *=|if.*IMPLAUSIBLE_FEE_SEK_PER_KWH|.*IMPLAUSIBLE_FEE_SEK_PER_KWH:g)"
