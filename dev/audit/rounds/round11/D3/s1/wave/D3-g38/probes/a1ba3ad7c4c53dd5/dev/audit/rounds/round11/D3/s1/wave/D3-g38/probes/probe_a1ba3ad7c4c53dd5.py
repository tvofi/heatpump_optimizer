#!/usr/bin/env python3
# Metric: whether _slab_series(usable) returns the series (1) or None (0) for N SysIdSample rows 30 min apart; inputs_differing counts N whose outcome differs.
# Command: HPO_PROBE_ROOT=<clean baseline checkout> PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g38/probes/probe_a1ba3ad7c4c53dd5.py
# EXPECTED inputs_differing=1 of 4 (N=6 rows -> exactly 5 intervals: baseline returns the series, mutant None)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g38 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_slab_series, sysid.py:875 `if len(dts) < 5:`
# Perturbation: key a1ba3ad7c4c53dd5, CMP_BOUND `< 5` -> `<= 5`, applied in memory (function re-compiled from the baseline source with the
#   one line replaced); the baseline arm is the same source re-compiled unchanged.
# Null control: N=5 (4 intervals: None in both), N=7 and N=12 (series in both)
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mutlib as L
from datetime import datetime, timedelta, timezone
m = L.module()
base, mut = L.mutant(m, "_slab_series", "    if len(dts) < 5:", "    if len(dts) <= 5:")
t0 = datetime(2026, 1, 10, 23, 0, tzinfo=timezone.utc)
def rows(n):
    return [m.SysIdSample(when=t0 + timedelta(minutes=30 * i), room_temp=21.0 + 0.05 * i, outdoor_temp=0.0,
                          power_kw=3.0, phase="step") for i in range(n)]
cases = [6, 5, 7, 12]
diff = 0
for n in cases:
    b, x = int(base(rows(n)) is not None), int(mut(rows(n)) is not None)
    diff += b != x
    print(f"RESULT series[N={n}] baseline={b} mutant={x}")
print(f"RESULT inputs_differing={diff} of {len(cases)}")
