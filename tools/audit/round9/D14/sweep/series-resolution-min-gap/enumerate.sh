#!/usr/bin/env bash
# D14 sweep, class "series resolution inferred from the minimum gap".
# Finding: D1-s5-04 (verified, low -- open_meteo.py:231 infers a time series' sample resolution
# as timedelta(seconds=min(gaps)); a single spurious small gap (duplicate/near-duplicate
# timestamp, out-of-order sample) collapses the inferred resolution far below the series' true
# spacing).
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
grep -n "min(gaps)\|resolution = timedelta\|sample_interval\|resolution =" custom_components/heatpump_optimizer/*.py
