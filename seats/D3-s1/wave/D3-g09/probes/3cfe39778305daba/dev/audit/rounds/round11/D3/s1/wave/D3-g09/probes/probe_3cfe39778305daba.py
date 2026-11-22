#!/usr/bin/env python3
# Metric: record_quiet_period calls (0/1) and the comfort learner's evidence change from one
#   HeatPumpOptimizerCoordinator._record_quiet_comfort_period() on a flat plan with prices 0.5/1.0/1.5, at planned
#   heating of exactly 1.0 kWh (4.0 kW over one 15-min step, the tie), 0.75 and 1.5 kWh.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_3cfe39778305daba.py
# EXPECTED RESULT calls_tie_baseline=1, calls_tie_mutant=0; null control: 0.75 kWh (both 0) and 1.5 kWh (both 1).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._record_quiet_comfort_period
#   (coordinator.py:11008 `if heating_kwh < 1.0:`).
# Perturbation: mutant 3cfe39778305daba, `< 1.0` -> `<= 1.0`, in memory. Direction: at exactly 1.0 kWh the quiet
#   period is no longer recorded.
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _quiet_common as Q  # noqa: E402

OLD = "if heating_kwh < 1.0:"
NEW = "if heating_kwh <= 1.0:"
MUT = L.mutant(Q.C, "_record_quiet_comfort_period", OLD, NEW)
prices = np.array([0.5, 1.0, 1.5])
for label, power in (("tie", [4.0]), ("kwh075", [3.0]), ("kwh150", [6.0]), ("tie_split", [2.0, 2.0])):
    for name, fn in (("baseline", None), ("mutant", MUT)):
        d, n, dt = Q.evidence_delta(prices, power, fn=fn)
        print(f"RESULT calls_{label}_{name}={n} evidence_delta={d} heating_kwh={sum(power) * dt}")
L.trailer()
