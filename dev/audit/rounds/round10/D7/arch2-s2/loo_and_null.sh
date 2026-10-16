#!/bin/bash
# ARCH2-s2: leave-one-out over the seven patches, and the rename null control.
#   PYTHONPATH=tests/hastub bash dev/audit/rounds/round10/D7/arch2-s2/loo_and_null.sh
# LOO: the union of six, each patch dropped in turn, on main and on main + ARCH-s1.
# Null: UNION then N0_rename_null.patch (two names renamed, nothing else) must read the union's delta_S.
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../../../.." && pwd)
cd "$ROOT"
PY=${PY:-python3}
ALL="P1_config_notices_owned P2_fixed_action_priced_whole P3_store_owns_its_digest P4_event_readings_published_whole P5_peak_billing_record P6_price_tile_rotation_owned P7_price_learner_owns_its_days"
for drop in $ALL; do
  keep=""
  for p in $ALL; do [ "$p" != "$drop" ] && keep="$keep $p.patch"; done
  m=$("$PY" "$HERE/arch2_delta.py" $keep | grep 'RESULT delta_S=')
  s=$("$PY" "$HERE/arch2_delta.py" $keep --on-s1 | grep 'RESULT delta_S=')
  echo "LOO drop $drop: main $m | s1 $s"
done
echo "NULL union+N0: $("$PY" "$HERE/arch2_delta.py" UNION_P1_P7.patch N0_rename_null.patch | grep 'RESULT delta_S=')"
