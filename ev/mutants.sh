#!/bin/bash
# reviewer-built: one-line mutants of legionella.py on a git-archive copy of the head; runs features.py + guard_pins.py
W=$1; R=$(git rev-parse --show-toplevel); H=a6c6bd8eaaae1acedcb8d25d6fdad5057573a5aa
F=custom_components/heatpump_optimizer/legionella.py
declare -A M
M[null]='1s/^/# reviewer null control\n/'
M[s349_CMP_BOUND]='349s/< self._retry_hours() \* 3600.0/<= self._retry_hours() * 3600.0/'
M[s354_CLAMP_DROP]='354s/max(peak, self.attempt_peak or peak)/(peak)/'
M[s60_CMP_BOUND]='60s/if age_h > interval_days/if age_h >= interval_days/'
M[s625_CMP_BOUND]='625s/<= 0)/< 0)/'
M[s625_GUARD_OFF]='625s/if attempt is None or .*:$/if False:/'
M[s659_BOOLOP]='659s/params.dhw_enabled and params.dhw_legionella_enabled/params.dhw_enabled or params.dhw_legionella_enabled/'
M[s662_GUARD_OFF]='662s/if days == self.overdue_notice:/if False:/'
M[s705_GUARD_OFF]='705s/if overdue_days is not None:/if False:/'
M[R4_x48]='60s/interval_days \* 24.0/interval_days * 48.0/'
for k in "${!M[@]}"; do (
  D=$W/mut/$k; mkdir -p $D; git -C $R archive $H | tar -x -C $D
  sed -i "${M[$k]}" $D/$F
  git -C $R show $H:$F | diff - $D/$F > $W/ev/mutant_$k.diff
  cd $D && { PYTHONPATH=tests/hastub timeout 1500 python3 tests/features.py 2>&1 | grep -E "FAIL|PASSED|FAILED" | tail -15; echo "--- guard_pins"; PYTHONPATH=tests/hastub timeout 600 python3 tests/guard_pins.py 2>&1 | tail -2; } > $W/ev/mutant_$k.txt 2>&1
  echo "done $k"
) & done; wait; echo ALLDONE
