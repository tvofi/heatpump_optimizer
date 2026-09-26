#!/usr/bin/env bash
# D14 sweep, class "staleness limit shorter than a report-on-change sensor's quiet interval".
# Finding: D1-s5-51 (verified, medium -- a report-on-change Indoor Temperature thermometer,
# silent (unchanged) for more than INPUT_MAX_AGE_MINUTES[indoor]=60 min, turns the Indoor
# Temperature entity unavailable although HA still holds a valid, merely-unchanged reading.
# Harness: tools/audit/round9/D1/leads/indoor_silence.py, re-run here: unavailable=4 of 7 silence
# cells (61/90/240/480 min), matching baseline exactly.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
echo "--- every keyed staleness limit ---"
grep -n 'INPUT_MAX_AGE_MINUTES\[' custom_components/heatpump_optimizer/const.py
echo "--- every entity whose availability follows the same _reading_key age gate ---"
grep -n '_reading_key = ' custom_components/heatpump_optimizer/sensor.py
echo "--- positive control (existing D1 harness) ---"
PYTHONPATH=tests/hastub python3 tools/audit/round9/D1/leads/indoor_silence.py
