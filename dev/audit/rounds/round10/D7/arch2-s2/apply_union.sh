#!/bin/bash
# ARCH2-s2: apply the seven prototype patches, in order, to the checkout this runs in (the union).
#   bash dev/audit/rounds/round10/D7/arch2-s2/apply_union.sh [-R]
# -R reverses them, last first. Each patch also applies alone on the baseline; the union composes
# them with git apply -C2: P7's init hunk ends one context line into P1's, and no hunk overlaps.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../../../.." && pwd)
cd "$ROOT"
PATCHES="P1_config_notices_owned P2_fixed_action_priced_whole P3_store_owns_its_digest P4_event_readings_published_whole P5_peak_billing_record P6_price_tile_rotation_owned P7_price_learner_owns_its_days"
if [ "$1" = "-R" ]; then
  for p in $(echo $PATCHES | tr ' ' '\n' | tail -r); do git apply -C2 -R "$HERE/$p.patch"; echo "reverted $p"; done
else
  for p in $PATCHES; do git apply -C2 "$HERE/$p.patch"; echo "applied $p"; done
fi
