#!/bin/bash
# usage: mini.sh <tree>  -- runs the R10-SETPOINT-POWER block of tests/features.py verbatim against <tree>
T=$1; F=$T/tests/features.py
S=$(grep -n "^# --- R10-SETPOINT-POWER" $F | cut -d: -f1); E=$(grep -n '^R.section("#1913 SW-4' $F | cut -d: -f1)
M=$(mktemp -d)/mini.py
{ sed -n 12,20p $F
  cat <<'P'
R = Results("mini")
from types import SimpleNamespace as _PaNS
from heatpump_optimizer import pump_arbiter as _pa
_PA_T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
from heatpump_optimizer.const import CONF_FLOW_HEAT_C as _PP_FLOW_KEY
P
  sed -n "${S},$((E-1))p" $F
  echo 'sys.exit(R.close("MINI CHECKS"))'
} > $M
cd $T && PYTHONPATH=tests/hastub:custom_components:tests python3 $M
