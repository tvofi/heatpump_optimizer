#!/usr/bin/env bash
# D14 sweep, class "live input with no physical-plausibility bound".
# Findings: D1-s1-03 (dhw_learning temp_drop/energy_kwh, no floor/ceiling), D1-s2-02 (weather
# forecast + ECL110 MQTT parsers, no per-sample plausibility bound -- see the finder's own
# harness, tools/audit/round9/D1/s2/parsers.py, reused here as the family-B positive control).
# This enumerator widens the seam rule to every site that parses a live external state to a
# float used downstream, across the package.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
echo "--- family A: DHW draw detector (temp_drop / energy_kwh) ---"
grep -n "temp_drop\|energy_kwh" custom_components/heatpump_optimizer/dhw_learning.py
echo "--- family B: weather forecast + ECL110 parsers (existing D1 harness) ---"
echo "harness: tools/audit/round9/D1/s2/parsers.py (poisoned_series / wedged metrics)"
echo "--- family C (widened): every other float(state.state) parse of a live entity ---"
grep -n "float(state\.state)\|float(new_state\.state)" custom_components/heatpump_optimizer/*.py
