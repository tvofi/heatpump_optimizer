#!/bin/bash
# ARCH2-s2: every delta this seat reports, re-executed. Writes out_<patch>_{main,revert,s1}.txt here.
#   PYTHONPATH=tests/hastub bash dev/audit/rounds/round10/D7/arch2-s2/run_all.sh
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../../../.." && pwd)
cd "$ROOT"
PY=${PY:-python3}
for p in P1_config_notices_owned P2_fixed_action_priced_whole P3_store_owns_its_digest \
         P4_event_readings_published_whole P5_peak_billing_record P6_price_tile_rotation_owned \
         P7_price_learner_owns_its_days UNION_P1_P7; do
  "$PY" "$HERE/arch2_delta.py" "$p.patch" > "$HERE/out_${p}_main.txt" 2>&1
  "$PY" "$HERE/arch2_delta.py" "$p.patch" --revert > "$HERE/out_${p}_revert.txt" 2>&1
  "$PY" "$HERE/arch2_delta.py" "$p.patch" --on-s1 > "$HERE/out_${p}_s1.txt" 2>&1
  printf '%-36s main %s | revert %s | s1 %s\n' "$p" \
    "$(grep -h 'RESULT delta_S=' "$HERE/out_${p}_main.txt")" \
    "$(grep -h 'RESULT delta_S=' "$HERE/out_${p}_revert.txt")" \
    "$(grep -h 'RESULT delta_S=' "$HERE/out_${p}_s1.txt")"
done
