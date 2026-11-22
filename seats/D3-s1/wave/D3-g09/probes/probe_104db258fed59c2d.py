#!/usr/bin/env python3
# Metric: record_quiet_period calls (0/1) and the comfort learner's evidence change from one
#   HeatPumpOptimizerCoordinator._record_quiet_comfort_period() on a flat plan, at a price vector whose float64
#   mean is exactly 1e-6 (the tie) with a spread >= 15 % of the mean and 1.5 kWh of planned heating.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_104db258fed59c2d.py
# EXPECTED RESULT calls_tie_baseline=0, calls_tie_mutant=1 (evidence -0.35*interval_days); null control: an
#   ordinary 0.5..1.5 price day, both arms 1 call and the same evidence change.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._record_quiet_comfort_period
#   (coordinator.py:11000 `if mean_price <= 1e-6:`).
# Perturbation: mutant 104db258fed59c2d, `<= 1e-6` -> `< 1e-6`, in memory. Direction: at a mean price of exactly
#   1e-6 a quiet period is recorded (evidence down) where the baseline skips it.
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _quiet_common as Q  # noqa: E402

OLD = "if mean_price <= 1e-6:"
NEW = "if mean_price < 1e-6:"
MUT = L.mutant(Q.C, "_record_quiet_comfort_period", OLD, NEW)
tie = Q.tie_search(1e-6, lambda v: float(np.mean(v)), [(0.5e-6, 1.5e-6), (0.8e-6, 1.0e-6, 1.2e-6), (0.7e-6, 1.3e-6)])
print(f"RESULT tie_prices={tie.tolist()} mean={float(np.mean(tie))!r} ratio={(tie.max()-tie.min())/np.mean(tie):.4f}")
power = [6.0]  # 6 kW for one 15-min step = 1.5 kWh
for label, prices in (("tie", tie), ("ordinary", np.array([0.5, 1.0, 1.5])), ("zero", np.zeros(2))):
    for name, fn in (("baseline", None), ("mutant", MUT)):
        d, n, dt = Q.evidence_delta(prices, power, fn=fn)
        print(f"RESULT calls_{label}_{name}={n} evidence_delta={d}")
L.trailer()
